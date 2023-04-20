from schemas.base_model import BaseModel


class CreateIconColor(BaseModel):
    icon_url: str
    color_code: str


class Icon(BaseModel):
    id: int
    url: str


class Color(BaseModel):
    id: int
    code: str


class IconColor(BaseModel):
    id: int
    icon: Icon
    color: Color
