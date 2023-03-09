import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from starlette import status
from starlette.exceptions import HTTPException

import schemas
import models


def create_group(
    db: Session, group: schemas.CreateGroup, user_id: int
) -> schemas.Group:
    db_group = models.Group(**group.dict(), admin_id=user_id)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    add_user_in_group(db, db_group.id, user_id)
    return db_group


def add_user_in_group(db: Session, group_id: int, user_id: int) -> None:
    db_user_group = models.UserGroup(
        user_id=user_id, group_id=group_id, date_join=datetime.date.today()
    )
    db.add(db_user_group)
    db.commit()
    db.refresh(db_user_group)


def read_users_group(db: Session, group_id: int, user_id: int) -> schemas.UsersGroup:
    try:
        (
            db.query(models.UserGroup)
            .filter(
                and_(
                    models.UserGroup.user_id == user_id,
                    models.UserGroup.group_id == group_id,
                )
            )
            .one()
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not in this group!",
        )
    db_query = (
        db.query(models.Group)
        .options(joinedload(models.Group.users_group))
        .where(models.Group.id == group_id)
        .one()
    )
    return db_query


def read_user_groups(db: Session, user_id: int) -> schemas.Group:
    db_query = (
        db.query(models.User)
        .options(joinedload(models.User.user_groups))
        .where(models.User.id == user_id)
        .one()
    )
    return db_query
