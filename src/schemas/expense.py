import datetime

from schemas import BaseUser, CategoryModel, ShortGroup
from schemas.base_model import BaseModel


class ExpenseCreate(BaseModel):
    descriptions: str
    amount: float
    category_id: int


class CategoryGroup(BaseModel):
    group: ShortGroup
    category: CategoryModel
    color_code: str
    icon_url: str


class ExpenseModel(BaseModel):
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
