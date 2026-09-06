from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SalaryStructureRule(Base):
    __tablename__ = "salary_structure_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    salary_structure_id: Mapped[int] = mapped_column(Integer, ForeignKey("salary_structures.id"), nullable=False)
    salary_rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("salary_rules.id"), nullable=False)

    salary_structure = relationship("SalaryStructure", back_populates="structure_rules")
    salary_rule = relationship("SalaryRule", back_populates="structure_rules")
