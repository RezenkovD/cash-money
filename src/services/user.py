from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce, sum

from models import Expense, Replenishment, User
from schemas import UserBalance


def get_user(db: Session, login: str) -> Optional[User]:
    return db.query(User).filter_by(login=login).one_or_none()


def calculate_user_balance(db: Session, user_id: int) -> UserBalance:
    (replenishments,) = db.query(
        coalesce(sum(Replenishment.amount).filter(Replenishment.user_id == user_id), 0)
    ).one()
    (expenses,) = db.query(
        coalesce(sum(Expense.amount).filter(Expense.user_id == user_id), 0)
    ).one()

    user_balance = replenishments - expenses
    user_balance = UserBalance(balance=user_balance)
    return user_balance
