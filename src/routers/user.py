from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database import get_db
from dependencies import get_current_user
import models
import schemas
import services

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=List[schemas.User])
def read_user_groups(db: Session = Depends(get_db)) -> List[schemas.User]:
    return db.query(models.User).all()


@router.get("/groups/", response_model=schemas.UserGroups)
def read_user_groups(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.UserGroups:
    return services.read_user_groups(db, current_user.id)
