import datetime

from schemas import BaseUser, ShortGroup, Category
from schemas.base_model import BaseModel


class CreateExpense(BaseModel):
    descriptions: str
    amount: float
    category_id: int


class CategoryGroup(BaseModel):
    group: ShortGroup
    category: Category


class BaseExpense(BaseModel):
    id: int
    descriptions: str
    amount: float
    time: datetime.datetime
    category_group: CategoryGroup
    user: BaseUser


class UserExpense(BaseModel):
    id: int
    descriptions: str
    amount: float
    time: datetime.datetime
    category_group: CategoryGroup
