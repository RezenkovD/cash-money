import enum
import datetime

from sqlalchemy import Column, Integer, Enum, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class ResponseStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DENIED = "denied"
    OVERDUE = "OVERDUE"


class UserResponse(str, enum.Enum):
    ACCEPTED = "accepted"
    DENIED = "denied"


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    creation_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    status = Column(String, Enum(ResponseStatus), nullable=False)

    group = relationship("Group", back_populates="invitations")
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
