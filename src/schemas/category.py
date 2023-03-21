from pydantic import BaseModel


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


class CreateCategory(OurBaseModel):
    title: str


class Category(CreateCategory):
    id: int
