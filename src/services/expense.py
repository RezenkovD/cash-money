import datetime
from typing import List, Optional

from pydantic.schema import date
from sqlalchemy import and_, exc, extract
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

import schemas
import models


def create_expense(
    db: Session, user_id: int, group_id: int, expense: schemas.CreateExpense
) -> schemas.BaseExpense:
    try:
        db_user_group = (
            db.query(models.UserGroup)
            .filter_by(group_id=group_id, user_id=user_id)
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a user of this group!",
        )
    if db_user_group.status == models.Status.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The user is not active in this group!",
        )
    try:
        db.query(models.CategoryGroups).filter_by(
            category_id=expense.category_id,
            group_id=group_id,
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The group has no such category!",
        )
    db_expense = models.Expense(**expense.dict())
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


def read_expenses(
    db: Session,
    user_id: int,
    group_id: Optional[int] = None,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[schemas.UserExpense]:
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    if group_id is not None:
        try:
            db.query(models.UserGroup).filter_by(
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
) -> List[schemas.UserExpense]:
    expenses = (
        db.query(models.Expense).filter_by(user_id=user_id, group_id=group_id).all()
    )
    return expenses


def read_expenses_by_group_month(
    db: Session, group_id: int, user_id: int, filter_date: date
) -> List[schemas.UserExpense]:
    expenses = (
        db.query(models.Expense)
        .filter(
            and_(
                models.Expense.user_id == user_id,
                models.Expense.group_id == group_id,
                extract("year", models.Expense.time) == filter_date.year,
                extract("month", models.Expense.time) == filter_date.month,
            )
        )
        .all()
    )
    return expenses


def read_expenses_by_group_time_range(
    db: Session, group_id: int, user_id: int, start_date: date, end_date: date
) -> List[schemas.UserExpense]:
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The start date cannot be older than the end date!",
        )
    expenses = (
        db.query(models.Expense)
        .filter(
            models.Expense.user_id == user_id,
            models.Expense.group_id == group_id,
            models.Expense.time >= start_date,
            models.Expense.time <= end_date,
        )
        .all()
    )
    return expenses


def read_expenses_all_time(db: Session, user_id: int) -> List[schemas.UserExpense]:
    expenses = (
        db.query(models.Expense)
        .filter_by(
            user_id=user_id,
        )
        .all()
    )
    return expenses


def read_expenses_month(
    db: Session, user_id: int, filter_date: date
) -> List[schemas.UserExpense]:
    expenses = (
        db.query(models.Expense)
        .filter(
            and_(
                models.Expense.user_id == user_id,
                extract("year", models.Expense.time) == filter_date.year,
                extract("month", models.Expense.time) == filter_date.month,
            )
        )
        .all()
    )
    return expenses


def read_expenses_time_range(
    db: Session, user_id: int, start_date: date, end_date: date
) -> List[schemas.UserExpense]:
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The start date cannot be older than the end date!",
        )
    expenses = (
        db.query(models.Expense)
        .filter(
            models.Expense.user_id == user_id,
            models.Expense.time >= start_date,
            models.Expense.time <= end_date,
        )
        .all()
    )
    return expenses
