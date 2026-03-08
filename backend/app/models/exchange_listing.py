from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class ExchangeListing(Base):
    __tablename__ = "exchange_listings"

    listing_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    exchange = Column(String(10), nullable=False)
    code = Column(String(20), nullable=False)

    company = relationship("Company", back_populates="exchange_listings")

    __table_args__ = (UniqueConstraint("exchange", "code", name="uq_exchange_code"),)
