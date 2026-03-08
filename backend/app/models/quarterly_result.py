from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class QuarterlyResult(Base):
    __tablename__ = "quarterly_results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    quarter = Column(String(20), nullable=False)
    period_end_date = Column(Date, nullable=False)
    revenue = Column(Numeric(15, 2))
    operating_expenses = Column(Numeric(15, 2))
    operating_profit = Column(Numeric(15, 2))
    depreciation = Column(Numeric(15, 2))
    interest = Column(Numeric(15, 2))
    profit_before_tax = Column(Numeric(15, 2))
    tax = Column(Numeric(15, 2))
    net_profit = Column(Numeric(15, 2))
    eps = Column(Numeric(10, 2))

    company = relationship("Company", back_populates="quarterly_results")

    __table_args__ = (
        UniqueConstraint("company_id", "quarter", name="uq_company_quarter"),
    )
