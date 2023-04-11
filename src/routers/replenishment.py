from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database import get_db
from dependencies import (
    get_current_user,
    transform_date_or_422,
    transform_exact_date_or_422,
)
from schemas import Replenishments, CreateReplenishments, UserReplenishments
from models import User
import services

router = APIRouter(
    prefix="/replenishments",
    tags=["replenishments"],
)


@router.post("/", response_model=Replenishments)
def create_replenishments(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    replenishments: CreateReplenishments,
) -> Replenishments:
    return services.create_replenishments(db, current_user.id, replenishments)


@router.get("/all-time/", response_model=List[UserReplenishments])
def read_replenishments_all_time(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserReplenishments]:
    return services.read_replenishments(db=db, user_id=current_user.id)


@router.get("/{year_month}/", response_model=List[UserReplenishments])
def read_replenishments_month(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year_month: str,
) -> List[UserReplenishments]:
    filter_date = transform_date_or_422(year_month)
    return services.read_replenishments(
        db=db, user_id=current_user.id, filter_date=filter_date
    )


@router.get("/{start_date}/{end_date}/", response_model=List[UserReplenishments])
def read_replenishments_time_range(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    start_date: str,
    end_date: str,
) -> List[UserReplenishments]:
    start_date = transform_exact_date_or_422(start_date)
    end_date = transform_exact_date_or_422(end_date)
    return services.read_replenishments(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )
