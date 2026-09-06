from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.salary_rule import SalaryRule
from app.schemas.salary_rule import SalaryRuleCreate, SalaryRuleOut

router = APIRouter(prefix="/rules", tags=["Salary Rules"])

@router.get("/", response_model=list[SalaryRuleOut])
async def list_rules(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(SalaryRule).order_by(SalaryRule.sequence))
    return result.scalars().all()

@router.post("/", response_model=SalaryRuleOut)
async def create_rule(rule_in: SalaryRuleCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    rule = SalaryRule(**rule_in.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule
