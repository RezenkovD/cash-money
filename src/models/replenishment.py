import datetime

from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Replenishment(Base):
    __tablename__ = "replenishments"

    id = Column(Integer, primary_key=True, index=True)
    descriptions = Column(String, nullable=False)
    amount = Column(DECIMAL, nullable=False)
    time = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="replenishments")
