from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)

    groups = relationship("CategoryGroups", back_populates="category")


class CategoryGroups(Base):
    __tablename__ = "categories_groups"

    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)

    category = relationship("Category", back_populates="groups")
    group = relationship("Group", back_populates="categories_group")