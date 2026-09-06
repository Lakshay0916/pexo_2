from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SalaryRuleBase(BaseModel):
    name: str
    code: str
    category: str
    sequence: int = 10
    calculation_type: str = "FIXED"
    amount: float = 0.0
    percentage: float = 0.0
    formula: Optional[str] = None

class SalaryRuleCreate(SalaryRuleBase):
    pass

class SalaryRuleOut(SalaryRuleBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
