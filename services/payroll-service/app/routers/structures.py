from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.salary_structure import SalaryStructure
from app.schemas.salary_structure import SalaryStructureCreate, SalaryStructureOut

router = APIRouter(prefix="/structures", tags=["Salary Structures"])

@router.get("/", response_model=list[SalaryStructureOut])
async def list_structures(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(SalaryStructure))
    return result.scalars().all()

@router.post("/", response_model=SalaryStructureOut)
async def create_structure(structure_in: SalaryStructureCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    struct = SalaryStructure(**structure_in.model_dump())
    db.add(struct)
    await db.commit()
    await db.refresh(struct)
    return struct
