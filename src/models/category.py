from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)

    groups = relationship("CategoryGroups", back_populates="category")


class CategoryGroups(Base):
    __tablename__ = "categories_groups"

    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    icon_url = Column(String, nullable=False)
    color_code = Column(String, nullable=False)

    category = relationship("Category", back_populates="groups")
    group = relationship("Group", back_populates="categories_group")
    expenses = relationship("Expense", back_populates="category_group")
