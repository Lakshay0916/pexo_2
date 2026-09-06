from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PayrunBase(BaseModel):
    name: str
    period_start: date
    period_end: date
    status: str = "DRAFT"

class PayrunCreate(PayrunBase):
    pass

class PayrunOut(PayrunBase):
    id: int
    total_cost: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
