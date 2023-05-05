from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import services
from database import get_db
from dependencies import get_current_user
from models import User
from schemas import (
    AboutUser,
    CategoriesGroup,
    CreateGroup,
    GroupModel,
    UsersGroup,
)

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


@router.post("/", response_model=GroupModel)
def create_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group: CreateGroup,
) -> GroupModel:
    return services.create_group(db, current_user.id, group)


@router.put("/{group_id}/", response_model=GroupModel)
def update_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group: CreateGroup,
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
    "/{group_id}/remove/{user_id}/",
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


@router.get("/{group_id}/categories/", response_model=CategoriesGroup)
def read_categories_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
) -> CategoriesGroup:
    return services.read_categories_group(db, current_user.id, group_id)
