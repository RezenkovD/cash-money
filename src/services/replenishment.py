import datetime
from typing import List, Optional

from pydantic.schema import date
from sqlalchemy import and_, extract, exc
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

from models import Replenishment
from schemas import ReplenishmentCreate, ReplenishmentModel, UserReplenishment


def create_replenishment(
    db: Session, user_id: int, replenishment: ReplenishmentCreate
) -> ReplenishmentModel:
    db_replenishment = Replenishment(**replenishment.dict())
    db_replenishment.user_id = user_id
    db_replenishment.time = datetime.datetime.utcnow()
    db.add(db_replenishment)
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while create replenishments",
        )
    else:
        return db_replenishment


def update_replenishment(
    db: Session, user_id: int, replenishment: ReplenishmentCreate, replenishment_id: int
):
    try:
        db.query(Replenishment).filter_by(id=replenishment_id, user_id=user_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="It's not your replenishment!",
        )
    db.query(Replenishment).filter_by(id=replenishment_id).update(
        values={**replenishment.dict()}
    )
    db_replenishment = db.query(Replenishment).filter_by(id=replenishment_id).one()
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while update replenishment",
        )
    else:
        return db_replenishment


def delete_replenishment(db: Session, user_id: int, replenishment_id: int):
    try:
        db.query(Replenishment).filter_by(id=replenishment_id, user_id=user_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="It's not your replenishment!",
        )
    db.query(Replenishment).filter_by(id=replenishment_id).delete()
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while delete replenishment",
        )


def read_replenishments(
    db: Session,
    user_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[UserReplenishment]:
    replenishments = read_replenishments_all_time(db, user_id)
    if filter_date:
        replenishments = read_replenishments_month(db, user_id, filter_date)
    elif start_date and end_date:
        replenishments = read_replenishments_time_range(
            db, user_id, start_date, end_date
        )
    return replenishments


def read_replenishments_all_time(db: Session, user_id: int) -> List[UserReplenishment]:
    replenishments = db.query(Replenishment).filter_by(
        user_id=user_id,
    )
    return replenishments


def read_replenishments_month(
    db: Session, user_id: int, filter_date: date
) -> List[UserReplenishment]:
    replenishments = db.query(Replenishment).filter(
        and_(
            Replenishment.user_id == user_id,
            extract("year", Replenishment.time) == filter_date.year,
            extract("month", Replenishment.time) == filter_date.month,
        )
    )
    return replenishments


def read_replenishments_time_range(
    db: Session, user_id: int, start_date: date, end_date: date
) -> List[UserReplenishment]:
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The start date cannot be older than the end date!",
        )
    replenishments = db.query(Replenishment).filter(
        Replenishment.user_id == user_id,
        Replenishment.time >= start_date,
        Replenishment.time <= end_date,
    )
    return replenishments
