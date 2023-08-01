from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import services
from database import get_db
from dependencies import get_current_user
from models import User
from schemas import UserBalance, UserModel

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=List[UserModel])
def read_users(db: Session = Depends(get_db)) -> List[UserModel]:
    return db.query(User).all()


@router.get("/user-balance/", response_model=UserBalance)
def read_user_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserBalance:
    return services.calculate_user_balance(db, current_user.id)


@router.get("/info/", response_model=UserModel)
def read_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserModel:
    return db.query(User).filter_by(id=current_user.id).one()
