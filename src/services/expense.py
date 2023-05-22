import datetime
from typing import List, Optional

from pydantic.schema import date
from sqlalchemy import and_, exc, extract
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

from models import CategoryGroup, Expense, UserGroup
from enums import GroupStatusEnum
from schemas import ExpenseCreate, ExpenseModel, UserExpense


def validate_input_data(
    db: Session,
    user_id: int,
    group_id: int,
    expense: ExpenseCreate = None,
    expense_id: int = None,
) -> None:
    try:
        db_user_group = (
            db.query(UserGroup).filter_by(group_id=group_id, user_id=user_id).one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a user of this group!",
        )
    if db_user_group.status == GroupStatusEnum.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The user is not active in this group!",
        )
    if expense:
        try:
            db.query(CategoryGroup).filter_by(
                category_id=expense.category_id,
                group_id=group_id,
            ).one()
        except exc.NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The group has no such category!",
            )
    if expense_id:
        try:
            db.query(Expense).filter_by(id=expense_id, user_id=user_id).one()
        except exc.NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="It's not your expense!",
            )


def create_expense(
    db: Session, user_id: int, group_id: int, expense: ExpenseCreate
) -> ExpenseModel:
    validate_input_data(db=db, user_id=user_id, group_id=group_id, expense=expense)
    db_expense = Expense(**expense.dict())
    db_expense.user_id = user_id
    db_expense.group_id = group_id
    db_expense.time = datetime.datetime.utcnow()
    db.add(db_expense)
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while create expense",
        )
    else:
        return db_expense


def update_expense(
    db: Session, user_id: int, group_id: int, expense: ExpenseCreate, expense_id: int
) -> ExpenseModel:
    validate_input_data(
        db=db,
        user_id=user_id,
        group_id=group_id,
        expense=expense,
        expense_id=expense_id,
    )
    db.query(Expense).filter_by(id=expense_id).update(values={**expense.dict()})
    db_expense = db.query(Expense).filter_by(id=expense_id).one()
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while update expense",
        )
    else:
        return db_expense


def delete_expense(db: Session, user_id: int, group_id: int, expense_id: int) -> None:
    validate_input_data(
        db=db, user_id=user_id, group_id=group_id, expense_id=expense_id
    )
    db.query(Expense).filter_by(id=expense_id).delete()
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while delete expense",
        )


def read_expenses(
    db: Session,
    user_id: int,
    group_id: Optional[int] = None,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[UserExpense]:
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    if group_id is not None:
        try:
            db.query(UserGroup).filter_by(
                group_id=group_id,
                user_id=user_id,
            ).one()
        except exc.NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not a user of this group!",
            )
        expenses = read_expenses_by_group_all_time(db, group_id, user_id)
        if filter_date:
            expenses = read_expenses_by_group_month(db, group_id, user_id, filter_date)
        elif start_date and end_date:
            expenses = read_expenses_by_group_time_range(
                db, group_id, user_id, start_date, end_date
            )
        return expenses
    expenses = read_expenses_all_time(db, user_id)
    if filter_date:
        expenses = read_expenses_month(db, user_id, filter_date)
    elif start_date and end_date:
        expenses = read_expenses_time_range(db, user_id, start_date, end_date)
    return expenses


def read_expenses_by_group_all_time(
    db: Session, group_id: int, user_id: int
) -> List[UserExpense]:
    expenses = db.query(Expense).filter_by(user_id=user_id, group_id=group_id).all()
    return expenses


def read_expenses_by_group_month(
    db: Session, group_id: int, user_id: int, filter_date: date
) -> List[UserExpense]:
    expenses = (
        db.query(Expense)
        .filter(
            and_(
                Expense.user_id == user_id,
                Expense.group_id == group_id,
                extract("year", Expense.time) == filter_date.year,
                extract("month", Expense.time) == filter_date.month,
            )
        )
        .all()
    )
    return expenses


def read_expenses_by_group_time_range(
    db: Session, group_id: int, user_id: int, start_date: date, end_date: date
) -> List[UserExpense]:
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The start date cannot be older than the end date!",
        )
    expenses = (
        db.query(Expense)
        .filter(
            Expense.user_id == user_id,
            Expense.group_id == group_id,
            Expense.time >= start_date,
            Expense.time <= end_date,
        )
        .all()
    )
    return expenses


def read_expenses_all_time(db: Session, user_id: int) -> List[UserExpense]:
    expenses = (
        db.query(Expense)
        .filter_by(
            user_id=user_id,
        )
        .all()
    )
    return expenses


def read_expenses_month(
    db: Session, user_id: int, filter_date: date
) -> List[UserExpense]:
    expenses = (
        db.query(Expense)
        .filter(
            and_(
                Expense.user_id == user_id,
                extract("year", Expense.time) == filter_date.year,
                extract("month", Expense.time) == filter_date.month,
            )
        )
        .all()
    )
    return expenses


def read_expenses_time_range(
    db: Session, user_id: int, start_date: date, end_date: date
) -> List[UserExpense]:
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The start date cannot be older than the end date!",
        )
    expenses = (
        db.query(Expense)
        .filter(
            Expense.user_id == user_id,
            Expense.time >= start_date,
            Expense.time <= end_date,
        )
        .all()
    )
    return expenses
