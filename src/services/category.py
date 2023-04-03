from sqlalchemy import exc
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

import schemas
import models


def create_category(
    db: Session, user_id: int, group_id: int, category: schemas.CreateCategory
) -> schemas.Category:
    try:
        group = db.query(models.Group).filter_by(id=group_id, admin_id=user_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not admin in this group!",
        )
    if group.status == models.Status.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Group is not active!",
        )
    db_category = (
        db.query(models.Category).filter_by(title=category.title.lower()).one_or_none()
    )
    if db_category is None:
        db_category = models.Category(title=category.title.lower())
        db.add(db_category)
        db.flush()
    else:
        db_category_group = (
            db.query(models.CategoryGroups)
            .filter_by(
                group_id=group_id,
                category_id=db_category.id,
            )
            .one_or_none()
        )
        if db_category_group:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="The category is already in this group!",
            )
    db_category_group = models.CategoryGroups(
        category_id=db_category.id, group_id=group_id
    )
    db.add(db_category_group)
    try:
        db.commit()
    except:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while create category",
        )
    else:
        return db_category
