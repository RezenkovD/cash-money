from schemas.base_model import BaseModel


class CreateCategory(BaseModel):
    title: str


class CategoryModel(CreateCategory):
    id: int
