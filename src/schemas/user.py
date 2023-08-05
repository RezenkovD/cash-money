from typing import Optional

from schemas.base_model import BaseModel


class BaseUser(BaseModel):
    id: int
    login: str


class UserModel(BaseUser):
    first_name: str
    last_name: str
    picture: Optional[str]


class UserTotalExpenses(BaseModel):
    amount: float
    percentage_increase: float
