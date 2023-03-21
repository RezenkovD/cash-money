import datetime
from typing import Union

from sqlalchemy import and_, exc
from sqlalchemy.orm import Session, joinedload
from starlette import status
from starlette.exceptions import HTTPException

import schemas
import models


def remove_user(
    db: Session, group_id: int, user_id: int, admin_id: int
) -> Union[schemas.AboutUsers, schemas.UsersGroup]:
    try:
        db.query(models.Group).filter(
            and_(models.Group.id == group_id, models.Group.admin_id == admin_id)
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not admin in this group!",
        )
    try:
        (
            db.query(models.UserGroup)
            .filter(
                and_(
                    models.UserGroup.user_id == user_id,
                    models.UserGroup.group_id == group_id,
                    models.UserGroup.status == models.Status.ACTIVE,
                )
            )
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The user is not active or does not exist in this group!",
        )
    if admin_id == user_id:
        return disband_group(db, group_id)
    else:
        return leave_group(db, group_id, user_id)


def disband_group(db: Session, group_id: int) -> schemas.UsersGroup:
    db_group = db.query(models.Group).filter_by(id=group_id).one()
    db_group.status = models.Status.INACTIVE
    db.commit()
    db_users_group = db.query(models.UserGroup).filter_by(group_id=group_id).all()
    for user in db_users_group:
        user.status = models.Status.INACTIVE
        db.commit()
    db_users_group = (
        db.query(models.Group)
        .options(joinedload(models.Group.users_group))
        .where(models.Group.id == group_id)
        .one()
    )
    return db_users_group


def leave_group(
    db: Session, group_id: int, user_id: int
) -> Union[schemas.AboutUsers, schemas.UsersGroup]:
    db_admin_group = (
        db.query(models.Group)
        .filter(and_(models.Group.id == group_id, models.Group.admin_id == user_id))
        .one_or_none()
    )
    if db_admin_group:
        return disband_group(db, group_id)
    try:
        db_user_group = (
            db.query(models.UserGroup)
            .filter(
                and_(
                    models.UserGroup.group_id == group_id,
                    models.UserGroup.user_id == user_id,
                )
            )
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group is not found",
        )
    db_user_group.status = models.Status.INACTIVE
    db.commit()
    return db_user_group


def create_group(
    db: Session, group: schemas.CreateGroup, user_id: int
) -> schemas.Group:
    db_group = models.Group(
        **group.dict(), admin_id=user_id, status=models.Status.ACTIVE
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    add_user_in_group(db, db_group.id, user_id)
    return db_group


def add_user_in_group(db: Session, group_id: int, user_id: int) -> None:
    db_user_group = (
        db.query(models.UserGroup)
        .filter(
            and_(
                models.UserGroup.user_id == user_id,
                models.UserGroup.group_id == group_id,
                models.UserGroup.status == models.Status.INACTIVE,
            )
        )
        .one_or_none()
    )
    if db_user_group:
        db_user_group.status = models.Status.ACTIVE
        db.commit()
        db.refresh(db_user_group)
    else:
        db_user_group = models.UserGroup(
            user_id=user_id,
            group_id=group_id,
            date_join=datetime.date.today(),
            status=models.Status.ACTIVE,
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


def read_user_groups(db: Session, user_id: int) -> schemas.UserGroups:
    db_query = (
        db.query(models.User)
        .options(joinedload(models.User.user_groups))
        .where(models.User.id == user_id)
        .one()
    )
    return db_query


def read_categories_group(db: Session, group_id: int, user_id: int) -> schemas.CategoriesGroup:
    try:
        db.query(models.UserGroup).filter(and_(
            models.UserGroup.group_id == group_id,
            models.UserGroup.user_id == user_id,
        )).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You are not a user of this group!",
        )
    db_query = (
        db.query(models.Group)
        .options(joinedload(models.Group.categories_group))
        .where(models.Group.id == group_id)
        .one()
    )
    return db_query
