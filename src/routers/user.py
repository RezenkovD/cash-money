from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import services
from database import get_db
from dependencies import get_current_user
from models import User
from schemas import CurrentBalance, UserGroups, UserModel

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=List[UserModel])
def read_users(db: Session = Depends(get_db)) -> List[UserModel]:
    return db.query(User).all()


@router.get("/groups/", response_model=UserGroups)
def read_user_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserGroups:
    return services.read_user_groups(db, current_user.id)


@router.get("/current-balance/", response_model=CurrentBalance)
def read_user_current_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CurrentBalance:
    return services.current_balance(db, current_user.id)
