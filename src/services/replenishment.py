import datetime
from typing import List, Optional

from pydantic.schema import date
from sqlalchemy import and_, extract
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

import schemas
import models


def create_replenishments(
    db: Session, user_id: int, replenishments: schemas.CreateReplenishments
) -> schemas.Replenishments:
    db_replenishments = models.Replenishment(**replenishments.dict())
    db_replenishments.user_id = user_id
    db_replenishments.time = datetime.datetime.utcnow()
    db.add(db_replenishments)
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while create replenishments",
        )
    else:
        return db_replenishments


def read_replenishments(
    db: Session,
    user_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[schemas.UserReplenishments]:
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    replenishments = read_replenishments_all_time(db, user_id)
    if filter_date:
        replenishments = read_replenishments_month(db, user_id, filter_date)
    elif start_date and end_date:
        replenishments = read_replenishments_time_range(
            db, user_id, start_date, end_date
        )
    return replenishments


def read_replenishments_all_time(
    db: Session, user_id: int
) -> List[schemas.UserReplenishments]:
    replenishments = (
        db.query(models.Replenishment)
        .filter_by(
            user_id=user_id,
        )
        .all()
    )
    return replenishments


def read_replenishments_month(
    db: Session, user_id: int, filter_date: date
) -> List[schemas.UserReplenishments]:
    replenishments = (
        db.query(models.Replenishment)
        .filter(
            and_(
                models.Replenishment.user_id == user_id,
                extract("year", models.Replenishment.time) == filter_date.year,
                extract("month", models.Replenishment.time) == filter_date.month,
            )
        )
        .all()
    )
    return replenishments


def read_replenishments_time_range(
    db: Session, user_id: int, start_date: date, end_date: date
) -> List[schemas.UserReplenishments]:
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The start date cannot be older than the end date!",
        )
    replenishments = (
        db.query(models.Replenishment)
        .filter(
            models.Replenishment.user_id == user_id,
            models.Replenishment.time >= start_date,
            models.Replenishment.time <= end_date,
        )
        .all()
    )
    return replenishments
