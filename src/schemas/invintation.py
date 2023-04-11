from pydantic.schema import date

from schemas import GroupModel, UserModel
from schemas.base_model import BaseModel


class CreateInvitation(BaseModel):
    recipient_id: int
    group_id: int


class BaseInvitation(BaseModel):
    id: int
    status: str
    group: GroupModel
    creation_time: date


class InvitationModel(BaseInvitation):
    recipient: UserModel
