import datetime

from sqlalchemy import and_, exc
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

import schemas
import models


def create_expense(
    db: Session, group_id: int, expense: schemas.CreateExpense, user_id: int
) -> schemas.BaseExpense:
    try:
        db_user_group = (
            db.query(models.UserGroup)
            .filter(
                and_(
                    models.UserGroup.group_id == group_id,
                    models.UserGroup.user_id == user_id,
                )
            )
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
        db.query(models.CategoryGroups).filter(
            and_(
                models.CategoryGroups.category_id == expense.category_id,
                models.CategoryGroups.group_id == group_id,
            )
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
    db.commit()
    db.refresh(db_expense)
    return db_expense
