from typing import Optional

from schemas.base_model import BaseModel


class BaseUser(BaseModel):
    id: int
    login: str


class User(BaseModel):
    id: int
    login: str
    first_name: str
    last_name: str
    picture: Optional[str]
