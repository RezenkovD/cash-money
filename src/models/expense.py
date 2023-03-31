import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DECIMAL,
    DateTime,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import relationship

from database import Base
from models import CategoryGroups


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    descriptions = Column(String, nullable=False)
    amount = Column(DECIMAL, nullable=False)
    time = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, index=True, nullable=False)
    category_id = Column(Integer, index=True, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            [group_id, category_id],
            [CategoryGroups.group_id, CategoryGroups.category_id],
        ),
        {},
    )

    user = relationship("User", back_populates="expenses")
    category_group = relationship("CategoryGroups", back_populates="expenses")
