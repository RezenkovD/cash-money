from datetime import date
from typing import List

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


class ShortGroup(BaseModel):
    id: int
    title: str


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
    group: BaseGroup
    status: str
    date_join: date


class UserGroups(BaseModel):
    user_groups: List[AboutGroup]


class AboutCategory(BaseModel):
    category: CategoryModel


class CategoriesGroup(BaseModel):
    categories_group: List[AboutCategory]
