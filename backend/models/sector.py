from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Sector(Base):
    __tablename__ = "sectors"

    sector_id = Column(Integer, primary_key=True, autoincrement=True)
    sector_name = Column(String(100), nullable=False, unique=True)

    industries = relationship("Industry", back_populates="sector")
