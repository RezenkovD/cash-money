from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import services
from database import get_db
from dependencies import get_current_user
from models import User
from schemas import (
    AboutUser,
    GroupCreate,
    GroupModel,
    UsersGroup,
    UserGroups,
)

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


@router.get("/", response_model=UserGroups)
def read_user_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserGroups:
    return services.read_user_groups(db, current_user.id)


@router.post("/", response_model=GroupModel)
def create_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group: GroupCreate,
) -> GroupModel:
    return services.create_group(db, current_user.id, group)


@router.put("/{group_id}/", response_model=GroupModel)
def update_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group: GroupCreate,
    group_id: int,
) -> GroupModel:
    return services.update_group(db, current_user.id, group, group_id)


@router.get("/{group_id}/users/", response_model=UsersGroup)
def read_users_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
) -> UsersGroup:
    return services.read_users_group(db, current_user.id, group_id)


@router.post("/{group_id}/leave/", response_model=Union[AboutUser, UsersGroup])
def leave_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
) -> Union[AboutUser, UsersGroup]:
    return services.leave_group(db, current_user.id, group_id)


@router.post(
    "/{group_id}/users/{user_id}/remove/",
    response_model=Union[AboutUser, UsersGroup],
)
def remove_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    user_id: int,
) -> Union[AboutUser, UsersGroup]:
    return services.remove_user(db, current_user.id, group_id, user_id)
