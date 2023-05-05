from schemas.base_model import BaseModel


class CreateCategory(BaseModel):
    title: str
    icon_url: str
    color_code: str


class CategoryModel(BaseModel):
    id: int
    title: str
