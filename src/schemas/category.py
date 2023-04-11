from schemas.base_model import BaseModel


class CreateCategory(BaseModel):
    title: str


class Category(CreateCategory):
    id: int
