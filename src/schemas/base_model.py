from pydantic import BaseModel as BM


class BaseModel(BM):
    class Config:
        orm_mode = True
