from typing import Optional

from sqlalchemy.orm import Session

from models import User


def get_user(db: Session, login: str) -> Optional[User]:
    return db.query(User).filter_by(login=login).one_or_none()
