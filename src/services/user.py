from typing import Union

from sqlalchemy.orm import Session

from models import User


def get_user(db: Session, login: str) -> Union[User, None]:
    return db.query(User).filter_by(login=login).one_or_none()
