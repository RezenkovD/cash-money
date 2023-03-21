from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database import get_db
from dependencies import get_current_user
import models
import schemas
import services


router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


@router.post("/{group_id}/", response_model=schemas.BaseExpense)
def create_expense(
    group_id: int,
    expense: schemas.CreateExpense,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.BaseExpense:
    return services.create_expense(db, group_id, expense, current_user.id)
