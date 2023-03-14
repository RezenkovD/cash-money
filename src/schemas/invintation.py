from pydantic import BaseModel
from pydantic.schema import date

from schemas import User, Group


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


class CreateInvitation(OurBaseModel):
    recipient_id: int
    group_id: int


class BaseInvitation(OurBaseModel):
    id: int
    status: str
    group: Group
    creation_time: date


class Invitation(BaseInvitation):
    recipient: User
