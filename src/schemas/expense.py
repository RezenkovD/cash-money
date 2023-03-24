import datetime

from pydantic import BaseModel

from schemas import BaseUser, ShortGroup, Category


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


class CreateExpense(OurBaseModel):
    descriptions: str
    amount: float
    category_id: int


class CategoryGroup(OurBaseModel):
    group: ShortGroup
    category: Category


class BaseExpense(OurBaseModel):
    id: int
    descriptions: str
    amount: float
    time: datetime.datetime
    category_group: CategoryGroup
    user: BaseUser


class UserExpense(OurBaseModel):
    id: int
    descriptions: str
    amount: float
    time: datetime.datetime
    category_group: CategoryGroup
