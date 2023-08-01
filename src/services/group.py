import datetime
from typing import Union

from sqlalchemy import exc, func
from sqlalchemy.orm import Session, joinedload
from starlette import status
from starlette.exceptions import HTTPException

from models import Group, User, UserGroup, Expense
from enums import GroupStatusEnum
from schemas import (
    AboutUser,
    CategoriesGroup,
    GroupCreate,
    GroupModel,
    UserGroups,
    UsersGroup,
    GroupInfo,
)


def read_group_info(db: Session, user_id: int, group_id: int) -> GroupInfo:
    try:
        (
            db.query(UserGroup)
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
    group = (
        db.query(Group).options(joinedload(Group.admin)).filter_by(id=group_id).one()
    )
    group_users_count = (
        db.query(func.count(UserGroup.user_id)).filter_by(group_id=group_id).scalar()
    )
    group_expenses_count = (
        db.query(func.count(Expense.id)).filter_by(group_id=group_id).scalar()
    )
    group_info = GroupInfo(
        id=group.id,
        title=group.title,
        description=group.description,
        status=group.status,
        icon_url=group.icon_url,
        color_code=group.color_code,
        admin=group.admin,
        members=group_users_count,
        expenses=group_expenses_count,
    )
    return group_info


def remove_user(
    db: Session, admin_id: int, group_id: int, user_id: int
) -> Union[AboutUser, UsersGroup]:
    try:
        db.query(Group).filter_by(id=group_id, admin_id=admin_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not admin in this group!",
        )
    try:
        (
            db.query(UserGroup)
            .filter_by(
                user_id=user_id,
                group_id=group_id,
                status=GroupStatusEnum.ACTIVE,
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


def disband_group(db: Session, group_id: int) -> UsersGroup:
    db_group = db.query(Group).filter_by(id=group_id).one()
    db_group.status = GroupStatusEnum.INACTIVE
    db.query(UserGroup).filter_by(group_id=group_id).update(
        {UserGroup.status: GroupStatusEnum.INACTIVE}
    )
    db_users_group = (
        db.query(Group)
        .options(joinedload(Group.users_group))
        .filter_by(id=group_id)
        .one()
    )
    return db_users_group


def leave_group(
    db: Session, user_id: int, group_id: int
) -> Union[AboutUser, UsersGroup]:
    db_admin_group = (
        db.query(Group).filter_by(id=group_id, admin_id=user_id).one_or_none()
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
            db.query(UserGroup)
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
    db_user_group.status = GroupStatusEnum.INACTIVE
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while leave group",
        )
    else:
        return db_user_group


def create_group(db: Session, user_id: int, group: GroupCreate) -> GroupModel:
    db_group = Group(
        **group.dict(),
        admin_id=user_id,
        status=GroupStatusEnum.ACTIVE,
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


def update_group(
    db: Session, user_id: int, group: GroupCreate, group_id: int
) -> GroupModel:
    try:
        db.query(Group).filter_by(id=group_id, admin_id=user_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not an admin of this group!",
        )
    db.query(Group).filter_by(id=group_id).update(values={**group.dict()})
    db_group = db.query(Group).filter_by(id=group_id).one()
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while update group",
        )
    else:
        return db_group


def add_user_in_group(db: Session, user_id: int, group_id: int) -> None:
    db_user_group = (
        db.query(UserGroup)
        .filter_by(
            user_id=user_id,
            group_id=group_id,
            status=GroupStatusEnum.INACTIVE,
        )
        .one_or_none()
    )
    if db_user_group:
        db_user_group.status = GroupStatusEnum.ACTIVE
    else:
        db_user_group = UserGroup(
            user_id=user_id,
            group_id=group_id,
            date_join=datetime.date.today(),
            status=GroupStatusEnum.ACTIVE,
        )
        db.add(db_user_group)


def read_users_group(db: Session, user_id: int, group_id: int) -> UsersGroup:
    try:
        (
            db.query(UserGroup)
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
        db.query(Group)
        .options(joinedload(Group.users_group))
        .filter_by(id=group_id)
        .one()
    )
    return db_query


def read_user_groups(db: Session, user_id: int) -> UserGroups:
    db_query = (
        db.query(User).options(joinedload(User.user_groups)).filter_by(id=user_id).one()
    )
    return db_query


def read_categories_group(db: Session, user_id: int, group_id: int) -> CategoriesGroup:
    try:
        db.query(UserGroup).filter_by(
            group_id=group_id,
            user_id=user_id,
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You are not a user of this group!",
        )
    db_query = (
        db.query(Group)
        .options(joinedload(Group.categories_group))
        .filter_by(id=group_id)
        .one()
    )
    return db_query
