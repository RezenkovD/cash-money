from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import services
from database import get_db
from dependencies import get_current_user
from models import User
from schemas import CategoryModel, CategoryCreate, IconColor

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.post("/{group_id}/", response_model=CategoryModel)
def create_category(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    category: CategoryCreate,
) -> CategoryModel:
    return services.create_category(db, current_user.id, group_id, category)


@router.put("/{group_id}/{category_id}", response_model=CategoryModel)
def update_category(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    icon_color: IconColor,
    category_id: int,
) -> CategoryModel:
    return services.update_category(
        db, current_user.id, group_id, icon_color, category_id
    )
