from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from starlette.status import HTTP_204_NO_CONTENT

import services
from database import get_db
from dependencies import (
    get_current_user,
    transform_date_or_422,
    transform_exact_date_or_422,
)
from models import User
from schemas import ExpenseCreate, ExpenseModel, UserExpense

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
)


@router.post("/group/{group_id}/", response_model=ExpenseModel)
def create_expense(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    expense: ExpenseCreate,
) -> ExpenseModel:
    return services.create_expense(db, current_user.id, group_id, expense)


@router.put("/group/{group_id}/{expense_id}/", response_model=ExpenseModel)
def update_expense(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    expense: ExpenseCreate,
    expense_id: int,
) -> ExpenseModel:
    return services.update_expense(db, current_user.id, group_id, expense, expense_id)


@router.delete("/group/{group_id}/{expense_id}/", status_code=HTTP_204_NO_CONTENT)
def delete_expense(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    expense_id: int,
) -> None:
    services.delete_expense(db, current_user.id, group_id, expense_id)


@router.get("/by-group/{group_id}/", response_model=List[UserExpense])
def read_expenses(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    year_month: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> List[UserExpense]:
    if year_month and (start_date or end_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot use filter_date with start_date or end_date",
        )
    elif (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Both start_date and end_date are required",
        )
    elif year_month:
        filter_date = transform_date_or_422(year_month)
        return services.read_expenses(
            db=db, user_id=current_user.id, group_id=group_id, filter_date=filter_date
        )
    elif start_date and end_date:
        start_date = transform_exact_date_or_422(start_date)
        end_date = transform_exact_date_or_422(end_date)
        return services.read_expenses(
            db=db,
            user_id=current_user.id,
            group_id=group_id,
            start_date=start_date,
            end_date=end_date,
        )
    else:
        return services.read_expenses(db=db, user_id=current_user.id, group_id=group_id)


@router.get("/", response_model=List[UserExpense])
def read_expenses(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year_month: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> List[UserExpense]:
    if year_month and (start_date or end_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot use filter_date with start_date or end_date",
        )
    elif (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Both start_date and end_date are required",
        )
    elif year_month:
        filter_date = transform_date_or_422(year_month)
        return services.read_expenses(
            db=db, user_id=current_user.id, filter_date=filter_date
        )
    elif start_date and end_date:
        start_date = transform_exact_date_or_422(start_date)
        end_date = transform_exact_date_or_422(end_date)
        return services.read_expenses(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
        )
    else:
        return services.read_expenses(db=db, user_id=current_user.id)
