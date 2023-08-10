from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

import services
from database import get_db
from dependencies import (
    get_current_user,
    transform_date_or_422,
    transform_exact_date_or_422,
    Page,
)
from models import User
from schemas import UserBalance, UserModel, UserTotalExpenses, UserTotalReplenishments

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=Page[UserModel])
def read_users(db: Session = Depends(get_db)) -> Page[UserModel]:
    return paginate(db, db.query(User))


@router.get("/user-balance/", response_model=UserBalance)
def read_user_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserBalance:
    return services.calculate_user_balance(db, current_user.id)


@router.get("/info/", response_model=UserModel)
def read_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserModel:
    return db.query(User).filter_by(id=current_user.id).one()


@router.get("/total-expenses/", response_model=UserTotalExpenses)
def read_user_total_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year_month: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> UserTotalExpenses:
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
        return services.user_total_expenses(
            db, current_user.id, filter_date=filter_date
        )
    elif start_date and end_date:
        start_date = transform_exact_date_or_422(start_date)
        end_date = transform_exact_date_or_422(end_date)
        return services.user_total_expenses(
            db,
            current_user.id,
            start_date=start_date,
            end_date=end_date,
        )
    else:
        return services.user_total_expenses(db, current_user.id)


@router.get("/total-replenishments/", response_model=UserTotalReplenishments)
def read_user_total_replenishments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year_month: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> UserTotalReplenishments:
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
        return services.user_total_replenishments(
            db, current_user.id, filter_date=filter_date
        )
    elif start_date and end_date:
        start_date = transform_exact_date_or_422(start_date)
        end_date = transform_exact_date_or_422(end_date)
        return services.user_total_replenishments(
            db,
            current_user.id,
            start_date=start_date,
            end_date=end_date,
        )
    else:
        return services.user_total_replenishments(db, current_user.id)
