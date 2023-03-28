from pydantic.schema import date

from schemas import User, Group
from schemas.base_model import BaseModel


class CreateInvitation(BaseModel):
    recipient_id: int
    group_id: int


class BaseInvitation(BaseModel):
    id: int
    status: str
    group: Group
    creation_time: date


class Invitation(BaseInvitation):
    recipient: User
