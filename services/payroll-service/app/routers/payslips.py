from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.payslip import Payslip
from app.schemas.payslip import PayslipOut

router = APIRouter(prefix="/payslips", tags=["Payslips"])

@router.get("/", response_model=list[PayslipOut])
async def list_payslips(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Payslip))
    return result.scalars().all()
