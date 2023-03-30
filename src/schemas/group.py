from datetime import date
from typing import List


from schemas import User
from schemas.base_model import BaseModel
from schemas.category import Category


class CreateGroup(BaseModel):
    title: str
    description: str


class BaseGroup(CreateGroup):
    status: str


class ShortGroup(BaseModel):
    id: int
    title: str


class Group(BaseGroup):
    id: int
    admin: User


class AboutUsers(BaseModel):
    user: User
    status: str
    date_join: date


class UsersGroup(BaseModel):
    users_group: List[AboutUsers]


class AboutGroup(BaseModel):
    group: BaseGroup
    status: str
    date_join: date


class UserGroups(BaseModel):
    user_groups: List[AboutGroup]


class AboutCategories(BaseModel):
    category: Category


class CategoriesGroup(BaseModel):
    categories_group: List[AboutCategories]
