from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Payslip(Base):
    __tablename__ = "payslips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    payrun_id: Mapped[int] = mapped_column(Integer, ForeignKey("payruns.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    contract_id: Mapped[int] = mapped_column(Integer, nullable=False)
    basic_salary: Mapped[float] = mapped_column(Float, default=0.0)
    gross_salary: Mapped[float] = mapped_column(Float, default=0.0)
    net_salary: Mapped[float] = mapped_column(Float, default=0.0)
    total_deductions: Mapped[float] = mapped_column(Float, default=0.0)
    pdf_url: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    payrun = relationship("Payrun", back_populates="payslips")
    lines = relationship("PayslipLine", back_populates="payslip")
