from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Industry(Base):
    __tablename__ = "industries"

    industry_id = Column(Integer, primary_key=True, autoincrement=True)
    industry_name = Column(String(150), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.sector_id"), nullable=False)

    sector = relationship("Sector", back_populates="industries")
    companies = relationship("Company", back_populates="industry")
