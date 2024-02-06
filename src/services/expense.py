import datetime
from typing import List, Optional, Union

from pydantic.schema import date
from sqlalchemy import and_, exc, extract
from sqlalchemy.orm import Session
from sqlalchemy import select
from starlette import status
from starlette.exceptions import HTTPException

from models import CategoryGroup, Expense, UserGroup
from enums import GroupStatusEnum
from schemas import ExpenseCreate, ExpenseModel, UserExpense, ExpenseUpdate


def validate_user_group(db: Session, user_id: int, group_id: int) -> UserGroup:
    try:
        db_user_group = (
            db.query(UserGroup).filter_by(group_id=group_id, user_id=user_id).one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a user of this group!",
        )
    return db_user_group


def validate_expense(
    db: Session,
    user_id: int,
    group_id: int,
    expense_id: int,
) -> None:
    try:
        db.query(Expense).filter_by(id=expense_id, user_id=user_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="It's not your expense!",
        )
    try:
        db.query(Expense).filter_by(
            id=expense_id, user_id=user_id, group_id=group_id
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The expense does not belong to this group!",
        )


def validate_expense_update(
    db: Session,
    user_id: int,
    group_id: int,
    expense: ExpenseUpdate,
) -> None:
    try:
        db_user_group = (
            db.query(UserGroup)
            .filter_by(group_id=expense.group_id, user_id=user_id)
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a user of the group specified to update expenses!",
        )
    if db_user_group.status == GroupStatusEnum.INACTIVE:
        if group_id != expense.group_id:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="The user is not active in group specified to update expenses!",
            )
    try:
        db.query(CategoryGroup).filter_by(
            category_id=expense.category_id,
            group_id=expense.group_id,
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The group specified to update expenses does not contain this category!",
        )


def create_expense(
    db: Session, user_id: int, group_id: int, expense: ExpenseCreate
) -> ExpenseModel:
    db_user_group = validate_user_group(db=db, user_id=user_id, group_id=group_id)
    if db_user_group.status == GroupStatusEnum.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The user is not active in this group!",
        )
    try:
        db.query(CategoryGroup).filter_by(
            category_id=expense.category_id,
            group_id=group_id,
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The group does not have such a category!",
        )
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
            detail="An error occurred while create expense",
        )
    else:
        return db_expense


def update_expense(
    db: Session, user_id: int, group_id: int, expense: ExpenseUpdate, expense_id: int
) -> ExpenseModel:
    validate_user_group(db=db, user_id=user_id, group_id=group_id)
    validate_expense(db=db, user_id=user_id, group_id=group_id, expense_id=expense_id)
    validate_expense_update(db=db, user_id=user_id, group_id=group_id, expense=expense)
    db.query(Expense).filter_by(id=expense_id).update(values={**expense.dict()})
    db_expense = db.query(Expense).filter_by(id=expense_id).one()
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while update expense",
        )
    else:
        return db_expense


def delete_expense(db: Session, user_id: int, group_id: int, expense_id: int) -> None:
    validate_user_group(db=db, user_id=user_id, group_id=group_id)
    validate_expense(db=db, user_id=user_id, group_id=group_id, expense_id=expense_id)
    db.query(Expense).filter_by(id=expense_id).delete()
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while delete expense",
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
    if group_id:
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
        expenses = select(Expense).filter_by(user_id=user_id, group_id=group_id)
    else:
        expenses = select(Expense).filter_by(
            user_id=user_id,
        )
    if filter_date:
        expenses = expenses.filter(
            and_(
                Expense.user_id == user_id,
                extract("year", Expense.time) == filter_date.year,
                extract("month", Expense.time) == filter_date.month,
            )
        )
    elif start_date and end_date:
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The start date cannot be older than the end date!",
            )
        expenses = expenses.filter(
            Expense.user_id == user_id,
            Expense.time >= start_date,
            Expense.time <= end_date,
        )
    return expenses
