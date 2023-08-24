from datetime import date, datetime
from typing import List, Optional

from schemas import UserModel
from schemas.base_model import BaseModel
from schemas.category import CategoryModel


class GroupCreate(BaseModel):
    title: str
    description: str
    icon_url: str
    color_code: str


class BaseGroup(BaseModel):
    id: int
    title: str
    description: str
    status: str
    icon_url: str
    color_code: str


class ShortGroup(BaseModel):
    id: int
    title: str
    color_code: str


class GroupModel(BaseGroup):
    id: int
    admin: UserModel


class AboutUser(BaseModel):
    user: UserModel
    status: str
    date_join: date


class UsersGroup(BaseModel):
    users_group: List[AboutUser]


class AboutGroup(BaseModel):
    group: GroupModel
    status: str
    date_join: date


class UserGroups(BaseModel):
    user_groups: List[AboutGroup]


class AboutCategory(BaseModel):
    category: CategoryModel
    icon_url: str
    color_code: str


class CategoriesGroup(BaseModel):
    categories_group: List[AboutCategory]


class GroupInfo(GroupModel):
    members: int
    expenses: int


class GroupHistory(BaseModel):
    id: int
    descriptions: str
    amount: float
    time: datetime
    category_id: Optional[int] = None
    color_code_category: Optional[str] = None
    title_category: Optional[str] = None
    user_id: int
    user_login: str
    user_first_name: str
    user_last_name: str
    user_picture: str


class GroupTotalExpenses(BaseModel):
    amount: float
    percentage_increase: float


class GroupUserTotalExpenses(BaseModel):
    amount: float
    percentage_increase: float


class UserSpender(BaseModel):
    id: int
    first_name: str
    last_name: str
    picture: Optional[str]
    amount: float


class GroupDailyExpenses(BaseModel):
    date: date
    amount: float
