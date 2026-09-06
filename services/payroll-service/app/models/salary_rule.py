from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SalaryRule(Base):
    __tablename__ = "salary_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # BASIC, ALLOWANCE, DEDUCTION, NET
    sequence: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    calculation_type: Mapped[str] = mapped_column(String(50), default="FIXED")  # FIXED, PERCENTAGE, FORMULA
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    percentage: Mapped[float] = mapped_column(Float, default=0.0)
    formula: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    structure_rules = relationship("SalaryStructureRule", back_populates="salary_rule")
