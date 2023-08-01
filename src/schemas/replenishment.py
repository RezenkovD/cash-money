import datetime

from schemas import BaseUser
from schemas.base_model import BaseModel


class ReplenishmentCreate(BaseModel):
    amount: float
    descriptions: str


class ReplenishmentModel(ReplenishmentCreate):
    id: int
    time: datetime.datetime
    user: BaseUser


class UserReplenishment(ReplenishmentCreate):
    id: int
    time: datetime.datetime


class UserBalance(BaseModel):
    balance: float
