from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Icon(Base):
    __tablename__ = "icons"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)

    icon_color = relationship("IconColor", back_populates="icon")


class Color(Base):
    __tablename__ = "colors"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)

    icon_color = relationship("IconColor", back_populates="color")


class IconColor(Base):
    __tablename__ = "icon_color"

    id = Column(Integer, primary_key=True, index=True)
    color_id = Column(Integer, ForeignKey("colors.id"), nullable=False)
    icon_id = Column(Integer, ForeignKey("icons.id"), nullable=False)

    icon = relationship("Icon", back_populates="icon_color")
    color = relationship("Color", back_populates="icon_color")
    group = relationship("Group", back_populates="icon_color")
