from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PayslipLineOut(BaseModel):
    id: int
    rule_code: str
    rule_name: str
    category: str
    sequence: int
    amount: float
    model_config = ConfigDict(from_attributes=True)

class PayslipOut(BaseModel):
    id: int
    payrun_id: int
    employee_id: int
    contract_id: int
    basic_salary: float
    gross_salary: float
    net_salary: float
    total_deductions: float
    pdf_url: Optional[str] = None
    status: str
    created_at: datetime
    lines: List[PayslipLineOut] = []
    model_config = ConfigDict(from_attributes=True)
