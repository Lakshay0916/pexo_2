from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_password,
)
from app.auth.models import AppUser, RefreshToken
from app.auth.schemas import TokenResponse, UserLogin, UserOut
from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _user_out(user: AppUser) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        employee_id=user.employee_id,
        # TODO: hydrate from hr-service's employee record once its models are
        # reconciled with schema.sql — for now the frontend falls back to email.
        full_name=None,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
    )


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/auth",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


async def _issue_tokens(user: AppUser, db: AsyncSession, response: Response) -> TokenResponse:
    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "roles": [role.name for role in user.roles],
    })

    refresh_token = create_refresh_token()
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    await db.commit()

    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, user=_user_out(user))


@router.post("/login", response_model=TokenResponse)
async def login(user_in: UserLogin, response: Response, db: Annotated[AsyncSession, Depends(get_db)]):
    # Pydantic's EmailStr lowercases the domain on validation, and email is
    # conventionally case-insensitive end to end — so compare case-insensitively
    # rather than relying on stored values happening to already be lowercase.
    result = await db.execute(select(AppUser).filter(func.lower(AppUser.email) == user_in.email.lower()))
    user = result.scalars().first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    return await _issue_tokens(user, db, response)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response, db: Annotated[AsyncSession, Depends(get_db)]):
    raw_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    token_hash = hash_token(raw_token)
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token_hash == token_hash))
    stored = result.scalars().first()

    if (
        not stored
        or stored.revoked_at is not None
        or stored.expires_at < datetime.now(timezone.utc)
    ):
        response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/auth")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalid or expired")

    stored.revoked_at = datetime.now(timezone.utc)

    user_result = await db.execute(select(AppUser).filter(AppUser.id == stored.user_id))
    user = user_result.scalars().first()
    if not user or not user.is_active:
        await db.commit()
        response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/auth")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account no longer active")

    return await _issue_tokens(user, db, response)


@router.post("/logout")
async def logout(request: Request, response: Response, db: Annotated[AsyncSession, Depends(get_db)]):
    raw_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if raw_token:
        token_hash = hash_token(raw_token)
        result = await db.execute(select(RefreshToken).filter(RefreshToken.token_hash == token_hash))
        stored = result.scalars().first()
        if stored and stored.revoked_at is None:
            stored.revoked_at = datetime.now(timezone.utc)
            await db.commit()

    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/auth")
    return {"detail": "logged out"}
