from typing import Union, List

from sqlalchemy.orm import Session
from sqlalchemy_utils.types import url

from models import User


def get_user(db: Session, login: str) -> Union[User, None]:
    return db.query(User).filter_by(login=login).one_or_none()


def get_users(db: Session) -> List[User]:
    return db.query(User).all()


def create_user(db: Session, login: str, first_name: str, last_name: str, picture: url) -> User:
    db_user = User(login=login, first_name=first_name, last_name=last_name, picture=picture)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
