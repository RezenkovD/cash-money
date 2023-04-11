from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import services
from database import get_db
from dependencies import get_current_user
from models import User
from schemas import Category, CreateCategory

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.post("/{group_id}/", response_model=Category)
def create_category(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    category: CreateCategory,
) -> Category:
    return services.create_category(db, current_user.id, group_id, category)
