from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import services
from database import get_db
from dependencies import (
    get_current_user,
    transform_date_or_422,
    transform_exact_date_or_422,
)
from models import User
from schemas import CreateReplenishment, Replenishment, UserReplenishment

router = APIRouter(
    prefix="/replenishments",
    tags=["replenishments"],
)


@router.post("/", response_model=Replenishment)
def create_replenishments(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    replenishments: CreateReplenishment,
) -> Replenishment:
    return services.create_replenishments(db, current_user.id, replenishments)


@router.get("/all-time/", response_model=List[UserReplenishment])
def read_replenishments_all_time(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserReplenishment]:
    return services.read_replenishments(db=db, user_id=current_user.id)


@router.get("/{year_month}/", response_model=List[UserReplenishment])
def read_replenishments_month(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year_month: str,
) -> List[UserReplenishment]:
    filter_date = transform_date_or_422(year_month)
    return services.read_replenishments(
        db=db, user_id=current_user.id, filter_date=filter_date
    )


@router.get("/{start_date}/{end_date}/", response_model=List[UserReplenishment])
def read_replenishments_time_range(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    start_date: str,
    end_date: str,
) -> List[UserReplenishment]:
    start_date = transform_exact_date_or_422(start_date)
    end_date = transform_exact_date_or_422(end_date)
    return services.read_replenishments(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )
