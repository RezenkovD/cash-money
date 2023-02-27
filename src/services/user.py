from sqlalchemy.orm import Session
from sqlalchemy_utils.types import url

import models


def get_user(db: Session, login: str):
    return db.query(models.User).filter_by(login=login).one_or_none()


def get_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, login: str, first_name: str, last_name: str, picture: url):
    db_user = models.User(login=login, first_name=first_name, last_name=last_name, picture=picture)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
