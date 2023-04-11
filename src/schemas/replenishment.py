import datetime

from schemas import BaseUser
from schemas.base_model import BaseModel


class CreateReplenishment(BaseModel):
    amount: float
    descriptions: str


class ReplenishmentModel(CreateReplenishment):
    id: int
    time: datetime.datetime
    user: BaseUser


class UserReplenishment(CreateReplenishment):
    time: datetime.datetime


class CurrentBalance(BaseModel):
    current_balance: float
