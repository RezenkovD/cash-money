import datetime
import enum

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from database import Base


class Status(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, Enum(Status), nullable=False)

    admin = relationship("User", back_populates="groups")
    users_group = relationship("UserGroup", back_populates="group")
    invitations = relationship("Invitation", back_populates="group")
    categories_group = relationship("CategoryGroups", back_populates="group")


class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    date_join = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    status = Column(String, Enum(Status), nullable=False)

    user = relationship("User", back_populates="user_groups")
    group = relationship("Group", back_populates="users_group")
