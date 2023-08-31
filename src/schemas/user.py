import datetime
from typing import Optional, List

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


class UserTotalReplenishments(BaseModel):
    amount: float
    percentage_increase: float


class UserHistory(BaseModel):
    id: int
    descriptions: str
    amount: float
    time: datetime.datetime
    category_id: Optional[int] = None
    group_id: Optional[int] = None
    color_code_category: Optional[str] = None
    title_category: Optional[str] = None
    title_group: Optional[str] = None
    color_code_group: Optional[str] = None


class UserDailyExpenses(BaseModel):
    date: datetime.date
    amount: float


class UserCategoryExpenses(BaseModel):
    id: int
    title: str
    amount: float


class CategoryExpenses(BaseModel):
    id: int
    title: str
    color_code: str
    icon_url: str
    amount: Optional[float] = None


class UserGroupExpenses(BaseModel):
    group_id: int
    group_title: str
    categories: List[CategoryExpenses]


class GroupMember(UserModel):
    count_expenses: int
    total_expenses: UserTotalExpenses
    best_category: Optional[CategoryExpenses] = None


class UserDailyExpensesDetail(BaseModel):
    date: datetime.date
    amount: float
    categories: List[CategoryExpenses]
