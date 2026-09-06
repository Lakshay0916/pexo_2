from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SalaryStructureBase(BaseModel):
    name: str
    code: str

class SalaryStructureCreate(SalaryStructureBase):
    pass

class SalaryStructureOut(SalaryStructureBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
