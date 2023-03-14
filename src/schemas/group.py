from datetime import date
from typing import List

from pydantic import BaseModel

from schemas import User


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


class CreateGroup(OurBaseModel):
    title: str
    description: str


class BaseGroup(CreateGroup):
    status: str


class Group(BaseGroup):
    id: int
    admin: User


class AboutUsers(OurBaseModel):
    user: User
    status: str
    date_join: date


class UsersGroup(OurBaseModel):
    users_group: List[AboutUsers]


class AboutGroups(OurBaseModel):
    group: BaseGroup
    status: str
    date_join: date


class UserGroups(OurBaseModel):
    user_groups: List[AboutGroups]
