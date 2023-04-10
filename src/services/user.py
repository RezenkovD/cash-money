from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from models import User, Replenishment, Expense
from schemas import CurrentBalance


def get_user(db: Session, login: str) -> Optional[User]:
    return db.query(User).filter_by(login=login).one_or_none()


def read_user_current_balance(db: Session, user_id: int) -> CurrentBalance:
    replenishments = (
        db.query(func.sum(Replenishment.amount))
        .filter_by(user_id=user_id)
        .one_or_none()
    )
    if replenishments[0] is None:
        replenishments = 0
    else:
        replenishments = replenishments[0]

    expenses = (
        db.query(func.sum(Expense.amount)).filter_by(user_id=user_id).one_or_none()
    )
    if expenses[0] is None:
        expenses = 0
    else:
        expenses = expenses[0]

    balance = replenishments - expenses
    balance = CurrentBalance(current_balance=balance)
    return balance
