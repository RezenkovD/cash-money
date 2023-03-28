from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database import get_db
from dependencies import get_current_user
import models
import schemas
import services


router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.post("/{group_id}/", response_model=schemas.Category)
def create_category(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group_id: int,
    category: schemas.CreateCategory,
) -> schemas.Category:
    return services.create_category(db, current_user.id, group_id, category)
