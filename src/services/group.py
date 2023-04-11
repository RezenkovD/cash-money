import datetime
from typing import Union

from sqlalchemy import exc
from sqlalchemy.orm import Session, joinedload
from starlette import status
from starlette.exceptions import HTTPException

import models
import schemas


def remove_user(
    db: Session, admin_id: int, group_id: int, user_id: int
) -> Union[schemas.AboutUser, schemas.UsersGroup]:
    try:
        db.query(models.Group).filter_by(id=group_id, admin_id=admin_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not admin in this group!",
        )
    try:
        (
            db.query(models.UserGroup)
            .filter_by(
                user_id=user_id,
                group_id=group_id,
                status=models.Status.ACTIVE,
            )
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The user is not active or does not exist in this group!",
        )
    if admin_id == user_id:
        try:
            db_users_group = disband_group(db, group_id)
            db.commit()
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"An error occurred while disband group",
            )
        else:
            return db_users_group
    else:
        try:
            db_user_group = leave_group(db, user_id, group_id)
            db.commit()
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"An error occurred while remove user",
            )
        else:
            return db_user_group


def disband_group(db: Session, group_id: int) -> schemas.UsersGroup:
    db_group = db.query(models.Group).filter_by(id=group_id).one()
    db_group.status = models.Status.INACTIVE
    db.query(models.UserGroup).filter_by(group_id=group_id).update(
        {models.UserGroup.status: models.Status.INACTIVE}
    )
    db_users_group = (
        db.query(models.Group)
        .options(joinedload(models.Group.users_group))
        .filter_by(id=group_id)
        .one()
    )
    return db_users_group


def leave_group(
    db: Session, user_id: int, group_id: int
) -> Union[schemas.AboutUser, schemas.UsersGroup]:
    db_admin_group = (
        db.query(models.Group).filter_by(id=group_id, admin_id=user_id).one_or_none()
    )
    if db_admin_group:
        try:
            db_users_group = disband_group(db, group_id)
            db.commit()
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"An error occurred while leave group",
            )
        else:
            return db_users_group
    try:
        db_user_group = (
            db.query(models.UserGroup)
            .filter_by(
                group_id=group_id,
                user_id=user_id,
            )
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group is not found",
        )
    db_user_group.status = models.Status.INACTIVE
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while leave group",
        )
    else:
        return db_user_group


def create_group(
    db: Session, user_id: int, group: schemas.CreateGroup
) -> schemas.Group:
    db_group = models.Group(
        **group.dict(), admin_id=user_id, status=models.Status.ACTIVE
    )
    db.add(db_group)
    try:
        db.flush()
        add_user_in_group(db, user_id, db_group.id)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while create group",
        )
    else:
        return db_group


def add_user_in_group(db: Session, user_id: int, group_id: int) -> None:
    db_user_group = (
        db.query(models.UserGroup)
        .filter_by(
            user_id=user_id,
            group_id=group_id,
            status=models.Status.INACTIVE,
        )
        .one_or_none()
    )
    if db_user_group:
        db_user_group.status = models.Status.ACTIVE
    else:
        db_user_group = models.UserGroup(
            user_id=user_id,
            group_id=group_id,
            date_join=datetime.date.today(),
            status=models.Status.ACTIVE,
        )
        db.add(db_user_group)


def read_users_group(db: Session, user_id: int, group_id: int) -> schemas.UsersGroup:
    try:
        (
            db.query(models.UserGroup)
            .filter_by(
                user_id=user_id,
                group_id=group_id,
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
        .filter_by(id=group_id)
        .one()
    )
    return db_query


def read_user_groups(db: Session, user_id: int) -> schemas.UserGroups:
    db_query = (
        db.query(models.User)
        .options(joinedload(models.User.user_groups))
        .filter_by(id=user_id)
        .one()
    )
    return db_query


def read_categories_group(
    db: Session, user_id: int, group_id: int
) -> schemas.CategoriesGroup:
    try:
        db.query(models.UserGroup).filter_by(
            group_id=group_id,
            user_id=user_id,
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You are not a user of this group!",
        )
    db_query = (
        db.query(models.Group)
        .options(joinedload(models.Group.categories_group))
        .filter_by(id=group_id)
        .one()
    )
    return db_query
