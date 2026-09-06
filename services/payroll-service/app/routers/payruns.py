from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.payrun import PayrunCreate, PayrunOut
from app.services.payrun_service import PayrunService

router = APIRouter(prefix="/payruns", tags=["Payrun Wizard"])

@router.get("/", response_model=list[PayrunOut])
async def list_payruns(db: Annotated[AsyncSession, Depends(get_db)]):
    service = PayrunService(db)
    return await service.list_payruns()

@router.post("/", response_model=PayrunOut)
async def create_payrun(payrun_in: PayrunCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    service = PayrunService(db)
    return await service.create_payrun(payrun_in)
