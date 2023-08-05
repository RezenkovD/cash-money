from typing import Optional, Union
from dateutil.relativedelta import relativedelta

from starlette import status
from starlette.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce, sum
from sqlalchemy import and_, exc, extract
from pydantic.schema import date

from models import Expense, Replenishment, User
from schemas import UserBalance, UserTotalExpenses, UserTotalReplenishments


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


def get_total_actions_for_month(
    db: Session,
    user_id: int,
    year: date,
    month: date,
    model: Union[Expense, Replenishment],
):
    return db.query(
        coalesce(
            sum(model.amount).filter(
                and_(
                    model.user_id == user_id,
                    extract("year", model.time) == year,
                    extract("month", model.time) == month,
                )
            ),
            0,
        )
    ).one()[0]


def get_total_actions_for_time_range(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
    model: Union[Expense, Replenishment],
):
    return db.query(
        coalesce(
            sum(model.amount).filter(
                and_(
                    model.user_id == user_id,
                    model.time >= start_date,
                    model.time <= end_date,
                )
            ),
            0,
        )
    ).one()[0]


def user_total_expenses(
    db: Session,
    user_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> UserTotalExpenses:
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    (amount,) = db.query(
        coalesce(sum(Expense.amount).filter(Expense.user_id == user_id), 0)
    ).one()
    percentage_increase = 0

    if filter_date:
        year, month = filter_date.year, filter_date.month
        amount = get_total_actions_for_month(db, user_id, year, month, Expense)

        filter_date = filter_date - relativedelta(months=1)
        previous_year, previous_month = filter_date.year, filter_date.month
        previous_month_amount = get_total_actions_for_month(
            db, user_id, previous_year, previous_month, Expense
        )

        if previous_month_amount != 0:
            percentage_increase = (
                amount - previous_month_amount
            ) / previous_month_amount

    elif start_date and end_date:
        amount = get_total_actions_for_time_range(
            db, user_id, start_date, end_date, Expense
        )

        days_difference = (end_date - start_date).days
        zero_date = start_date - relativedelta(days=days_difference)
        previous_days_amount = get_total_actions_for_time_range(
            db, user_id, zero_date, start_date, Expense
        )

        if previous_days_amount != 0:
            percentage_increase = (amount - previous_days_amount) / previous_days_amount

    total_expenses = UserTotalExpenses(
        amount=amount, percentage_increase=percentage_increase
    )
    return total_expenses
