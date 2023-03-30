from typing import Union

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database import get_db
from dependencies import get_current_user
import models
import schemas
import services


router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


@router.post("/", response_model=schemas.Group)
def create_group(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group: schemas.CreateGroup,
) -> schemas.Group:
    return services.create_group(db, current_user.id, group)


@router.get("/{group_id}/users/", response_model=schemas.UsersGroup)
def read_users_group(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group_id: int,
) -> schemas.UsersGroup:
    return services.read_users_group(db, current_user.id, group_id)


@router.post(
    "/{group_id}/leave/", response_model=Union[schemas.AboutUsers, schemas.UsersGroup]
)
def leave_group(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group_id: int,
) -> Union[schemas.AboutUsers, schemas.UsersGroup]:
    return services.leave_group(db, current_user.id, group_id)


@router.post(
    "/{group_id}/remove/{user_id}/",
    response_model=Union[schemas.AboutUsers, schemas.UsersGroup],
)
def remove_user(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group_id: int,
    user_id: int,
) -> Union[schemas.AboutUsers, schemas.UsersGroup]:
    return services.remove_user(db, current_user.id, group_id, user_id)


@router.get("/{group_id}/categories/", response_model=schemas.CategoriesGroup)
def read_categories_group(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    group_id: int,
) -> schemas.CategoriesGroup:
    return services.read_categories_group(db, current_user.id, group_id)
