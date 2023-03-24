from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database import get_db
from dependencies import get_current_user, transform_date_or_422
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


@router.get("/{group_id}/all-time/", response_model=List[schemas.UserExpense])
def read_expenses_by_group_all_time(
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.UserExpense]:
    return services.read_expenses_by_group(db, group_id, current_user.id)


@router.get("/{group_id}/{year_month}/", response_model=List[schemas.UserExpense])
def read_expenses_by_group_month(
    year_month: str,
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.UserExpense]:
    filter_date = transform_date_or_422(year_month)
    return services.read_expenses_by_group(db, group_id, current_user.id, filter_date)
