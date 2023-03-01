from pydantic import BaseModel


class User(BaseModel):
    login: str
    first_name: str
    last_name: str
    picture: str

    class Config:
        orm_mode = True
