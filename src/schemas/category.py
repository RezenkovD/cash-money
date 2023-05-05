from schemas.base_model import BaseModel


class IconColor(BaseModel):
    icon_url: str
    color_code: str


class CreateCategory(IconColor):
    title: str


class CategoryModel(BaseModel):
    id: int
    title: str
