import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ResponseStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DENIED = "DENIED"
    OVERDUE = "OVERDUE"


class UserResponse(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    DENIED = "DENIED"


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    creation_time = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    status = Column(String, Enum(ResponseStatus), nullable=False)

    group = relationship("Group", back_populates="invitations")
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
