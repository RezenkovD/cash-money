from pydantic import BaseModel
from sqlalchemy_utils.types import url


class User(BaseModel):
    login: str
    first_name: str
    last_name: str
    picture: url

    class Config:
        orm_mode = True
