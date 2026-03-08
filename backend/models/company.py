from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Company(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), nullable=False)
    industry_id = Column(
        Integer, ForeignKey("industries.industry_id"), nullable=False
    )

    industry = relationship("Industry", back_populates="companies")
    exchange_listings = relationship(
        "ExchangeListing", back_populates="company"
    )
    quarterly_results = relationship(
        "QuarterlyResult", back_populates="company"
    )
