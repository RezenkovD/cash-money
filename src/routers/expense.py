from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database import get_db
from dependencies import (
    get_current_user,
    transform_date_or_422,
    transform_exact_date_or_422,
)
import models
import schemas
import services


router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


@router.post("/group/{group_id}/", response_model=schemas.BaseExpense)
def create_expense(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group_id: int,
    expense: schemas.CreateExpense,
) -> schemas.BaseExpense:
    return services.create_expense(db, current_user.id, group_id, expense)


@router.get("/group/{group_id}/all-time/", response_model=List[schemas.UserExpense])
def read_expenses_by_group_all_time(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group_id: int,
) -> List[schemas.UserExpense]:
    return services.read_expenses(db=db, user_id=current_user.id, group_id=group_id)


@router.get("/group/{group_id}/{year_month}/", response_model=List[schemas.UserExpense])
def read_expenses_by_group_month(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group_id: int,
    year_month: str,
) -> List[schemas.UserExpense]:
    filter_date = transform_date_or_422(year_month)
    return services.read_expenses(
        db=db, user_id=current_user.id, group_id=group_id, filter_date=filter_date
    )


@router.get(
    "/group/{group_id}/{start_date}/{end_date}/",
    response_model=List[schemas.UserExpense],
)
def read_expenses_by_group_time_range(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group_id: int,
    start_date: str,
    end_date: str,
) -> List[schemas.UserExpense]:
    start_date = transform_exact_date_or_422(start_date)
    end_date = transform_exact_date_or_422(end_date)
    return services.read_expenses(
        db=db,
        user_id=current_user.id,
        group_id=group_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/all-time/", response_model=List[schemas.UserExpense])
def read_expenses_all_time(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> List[schemas.UserExpense]:
    return services.read_expenses(db=db, user_id=current_user.id)


@router.get("/{year_month}/", response_model=List[schemas.UserExpense])
def read_expenses_month(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    year_month: str,
) -> List[schemas.UserExpense]:
    filter_date = transform_date_or_422(year_month)
    return services.read_expenses(
        db=db, user_id=current_user.id, filter_date=filter_date
    )


@router.get("/{start_date}/{end_date}/", response_model=List[schemas.UserExpense])
def read_expenses_time_range(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    start_date: str,
    end_date: str,
) -> List[schemas.UserExpense]:
    start_date = transform_exact_date_or_422(start_date)
    end_date = transform_exact_date_or_422(end_date)
    return services.read_expenses(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )
