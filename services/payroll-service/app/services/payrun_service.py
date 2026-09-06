from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payrun import Payrun
from app.schemas.payrun import PayrunCreate


class PayrunService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_payruns(self):
        result = await self.db.execute(select(Payrun))
        return result.scalars().all()

    async def create_payrun(self, payrun_in: PayrunCreate) -> Payrun:
        payrun = Payrun(**payrun_in.model_dump())
        self.db.add(payrun)
        await self.db.commit()
        await self.db.refresh(payrun)
        return payrun
