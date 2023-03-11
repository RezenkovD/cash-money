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
    group: schemas.CreateGroup,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.Group:
    return services.create_group(db, group, current_user.id)


@router.get("/{group_id}/users/", response_model=schemas.UsersGroup)
def read_users_group(
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.UsersGroup:
    return services.read_users_group(db, group_id, current_user.id)
