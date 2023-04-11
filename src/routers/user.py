from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas
import services
from database import get_db
from dependencies import get_current_user
from models import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)) -> List[schemas.User]:
    return db.query(User).all()


@router.get("/groups/", response_model=schemas.UserGroups)
def read_user_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.UserGroups:
    return services.read_user_groups(db, current_user.id)


@router.get("/current-balance/", response_model=schemas.CurrentBalance)
def read_user_current_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.CurrentBalance:
    return services.read_user_current_balance(db, current_user.id)
