from pydantic import BaseModel as BaseSchema


class BaseModel(BaseSchema):
    class Config:
        orm_mode = True
