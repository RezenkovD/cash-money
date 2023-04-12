from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

import services
from database import get_db
from dependencies import (
    get_current_user,
    transform_date_or_422,
    transform_exact_date_or_422,
)
from models import User
from schemas import CreateReplenishment, ReplenishmentModel, UserReplenishment

router = APIRouter(
    prefix="/replenishments",
    tags=["replenishments"],
)


@router.post("/", response_model=ReplenishmentModel)
def create_replenishments(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    replenishments: CreateReplenishment,
) -> ReplenishmentModel:
    return services.create_replenishments(db, current_user.id, replenishments)


@router.get("/", response_model=List[UserReplenishment])
def read_replenishments(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year_month: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> List[UserReplenishment]:
    if year_month and (start_date or end_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot use filter_date with start_date or end_date",
        )
    elif (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both start_date and end_date are required",
        )
    else:
        if year_month:
            filter_date = transform_date_or_422(year_month)
            return services.read_replenishments(
                db=db, user_id=current_user.id, filter_date=filter_date
            )
        elif start_date and end_date:
            start_date = transform_exact_date_or_422(start_date)
            end_date = transform_exact_date_or_422(end_date)
            return services.read_replenishments(
                db=db,
                user_id=current_user.id,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            return services.read_replenishments(db=db, user_id=current_user.id)
