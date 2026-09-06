from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payslip import Payslip


class PayslipService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_payrun(self, payrun_id: int):
        result = await self.db.execute(select(Payslip).filter(Payslip.payrun_id == payrun_id))
        return result.scalars().all()
