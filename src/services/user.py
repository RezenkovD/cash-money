from typing import Optional, Union, List
from dateutil.relativedelta import relativedelta

from starlette import status
from starlette.exceptions import HTTPException
from sqlalchemy import select, union, literal, desc, func
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce, sum
from sqlalchemy import and_, exc, extract
from pydantic.schema import date

from models import (
    Expense,
    Replenishment,
    User,
    CategoryGroup,
    Category,
    Group,
    UserGroup,
)
from schemas import (
    UserBalance,
    UserTotalExpenses,
    UserTotalReplenishments,
    UserHistory,
    UserDailyExpenses,
    UserCategoryExpenses,
    UserGroupExpenses,
)


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


def read_group_expenses(
    db: Session,
    user_id: int,
    group_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> UserGroupExpenses:
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    try:
        (
            db.query(UserGroup)
            .filter_by(
                user_id=user_id,
                group_id=group_id,
            )
            .one()
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not in this group!",
        )
    group_info = db.query(Group.id, Group.title).filter_by(id=group_id).one()
    from sqlalchemy import and_

    group_expenses = (
        db.query(
            Category.id.label("id"),
            Category.title.label("title"),
            CategoryGroup.color_code.label("color_code"),
            CategoryGroup.icon_url.label("icon_url"),
            func.sum(Expense.amount).label("amount"),
        )
        .join(Category, Expense.category_id == Category.id)
        .join(
            CategoryGroup,
            and_(
                Expense.category_id == CategoryGroup.category_id,
                Expense.group_id == CategoryGroup.group_id,
            ),
        )
        .filter(Expense.user_id == user_id, Expense.group_id == group_id)
        .group_by(
            Category.id,
            Category.title,
            CategoryGroup.color_code,
            CategoryGroup.icon_url,
        )
        .all()
    )
    if filter_date:
        group_expenses = (
            db.query(
                Category.id.label("id"),
                Category.title.label("title"),
                CategoryGroup.color_code.label("color_code"),
                CategoryGroup.icon_url.label("icon_url"),
                func.sum(Expense.amount).label("amount"),
            )
            .join(Category, Expense.category_id == Category.id)
            .join(
                CategoryGroup,
                and_(
                    Expense.category_id == CategoryGroup.category_id,
                    Expense.group_id == CategoryGroup.group_id,
                ),
            )
            .filter(
                and_(
                    Expense.user_id == user_id,
                    Expense.group_id == group_id,
                    extract("year", Expense.time) == filter_date.year,
                    extract("month", Expense.time) == filter_date.month,
                )
            )
            .group_by(
                Category.id,
                Category.title,
                CategoryGroup.color_code,
                CategoryGroup.icon_url,
            )
            .all()
        )
    elif start_date and end_date:
        group_expenses = (
            db.query(
                Category.id.label("id"),
                Category.title.label("title"),
                CategoryGroup.color_code.label("color_code"),
                CategoryGroup.icon_url.label("icon_url"),
                func.sum(Expense.amount).label("amount"),
            )
            .join(Category, Expense.category_id == Category.id)
            .join(
                CategoryGroup,
                and_(
                    Expense.category_id == CategoryGroup.category_id,
                    Expense.group_id == CategoryGroup.group_id,
                ),
            )
            .filter(
                and_(
                    Expense.user_id == user_id,
                    Expense.group_id == group_id,
                    Expense.time >= start_date,
                    Expense.time <= end_date,
                )
            )
            .group_by(
                Category.id,
                Category.title,
                CategoryGroup.color_code,
                CategoryGroup.icon_url,
            )
            .all()
        )
    user_group_expenses = UserGroupExpenses(
        group_id=group_info.id,
        group_title=group_info.title,
        categories=group_expenses,
    )
    return user_group_expenses


def read_category_expenses(
    db: Session,
    user_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> UserCategoryExpenses:
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    category_expenses = (
        db.query(
            Category.id.label("id"),
            Category.title.label("title"),
            func.sum(Expense.amount).label("amount"),
        )
        .join(Category, Expense.category_id == Category.id)
        .filter(Expense.user_id == user_id)
        .group_by(Category.id, Category.title)
        .all()
    )
    if filter_date:
        category_expenses = (
            db.query(
                Category.id.label("id"),
                Category.title.label("title"),
                func.sum(Expense.amount).label("amount"),
            )
            .join(Category, Expense.category_id == Category.id)
            .filter(
                and_(
                    user_id == user_id,
                    extract("year", Expense.time) == filter_date.year,
                    extract("month", Expense.time) == filter_date.month,
                )
            )
            .group_by(Category.id, Category.title)
            .all()
        )
    elif start_date and end_date:
        category_expenses = (
            db.query(
                Category.id.label("id"),
                Category.title.label("title"),
                func.sum(Expense.amount).label("amount"),
            )
            .join(Category, Expense.category_id == Category.id)
            .filter(
                and_(
                    user_id == user_id,
                    Expense.time >= start_date,
                    Expense.time <= end_date,
                )
            )
            .group_by(Category.id, Category.title)
            .all()
        )
    return category_expenses


def user_history(user_id: int) -> List[UserHistory]:
    history = (
        select(
            Expense.id,
            Expense.descriptions,
            Expense.amount,
            Expense.time,
            Expense.category_id,
            Expense.group_id,
            CategoryGroup.color_code.label("color_code_category"),
            Category.title.label("title_category"),
            Group.title.label("title_group"),
            Group.color_code.label("color_code_group"),
        )
        .join(CategoryGroup, Expense.category_id == CategoryGroup.category_id)
        .join(Group, Expense.group_id == Group.id)
        .join(Category, CategoryGroup.category_id == Category.id)
        .filter(Expense.user_id == user_id)
        .union(
            select(
                Replenishment.id,
                Replenishment.descriptions,
                Replenishment.amount,
                Replenishment.time,
                None,
                None,
                None,
                None,
                None,
                None,
            ).filter(Replenishment.user_id == user_id)
        )
        .order_by(desc(Replenishment.time))
    )
    return history


def read_user_daily_expenses(
    db: Session,
    user_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[UserDailyExpenses]:
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    daily_expenses = (
        db.query(
            func.date(Expense.time).label("date"),
            func.sum(Expense.amount).label("amount"),
        )
        .filter_by(user_id=user_id)
        .group_by(func.date(Expense.time))
        .all()
    )
    if filter_date:
        daily_expenses = (
            db.query(
                func.date(Expense.time).label("date"),
                func.sum(Expense.amount).label("amount"),
            )
            .filter(
                and_(
                    user_id == user_id,
                    extract("year", Expense.time) == filter_date.year,
                    extract("month", Expense.time) == filter_date.month,
                )
            )
            .group_by(func.date(Expense.time))
            .all()
        )
    elif start_date and end_date:
        daily_expenses = (
            db.query(
                func.date(Expense.time).label("date"),
                func.sum(Expense.amount).label("amount"),
            )
            .filter(
                and_(
                    user_id == user_id,
                    Expense.time >= start_date,
                    Expense.time <= end_date,
                )
            )
            .group_by(func.date(Expense.time))
            .all()
        )
    return daily_expenses


def get_total_actions_for_month(
    db: Session,
    user_id: int,
    year: date,
    month: date,
    model: Union[Expense, Replenishment],
) -> float:
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
) -> float:
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


def user_total_replenishments(
    db: Session,
    user_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> UserTotalReplenishments:
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    (amount,) = db.query(
        coalesce(sum(Replenishment.amount).filter(Replenishment.user_id == user_id), 0)
    ).one()
    percentage_increase = 0

    if filter_date:
        year, month = filter_date.year, filter_date.month
        amount = get_total_actions_for_month(db, user_id, year, month, Replenishment)

        filter_date = filter_date - relativedelta(months=1)
        previous_year, previous_month = filter_date.year, filter_date.month
        previous_month_amount = get_total_actions_for_month(
            db, user_id, previous_year, previous_month, Replenishment
        )

        if previous_month_amount != 0:
            percentage_increase = (
                amount - previous_month_amount
            ) / previous_month_amount

    elif start_date and end_date:
        amount = get_total_actions_for_time_range(
            db, user_id, start_date, end_date, Replenishment
        )

        days_difference = (end_date - start_date).days
        zero_date = start_date - relativedelta(days=days_difference)
        previous_days_amount = get_total_actions_for_time_range(
            db, user_id, zero_date, start_date, Replenishment
        )

        if previous_days_amount != 0:
            percentage_increase = (amount - previous_days_amount) / previous_days_amount

    total_replenishments = UserTotalReplenishments(
        amount=amount, percentage_increase=percentage_increase
    )
    return total_replenishments
