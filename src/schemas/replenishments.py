import datetime

from schemas import BaseUser
from schemas.base_model import BaseModel


class CreateReplenishments(BaseModel):
    amount: float
    descriptions: str


class Replenishments(CreateReplenishments):
    id: int
    time: datetime.datetime
    user: BaseUser


class UserReplenishments(CreateReplenishments):
    time: datetime.datetime
