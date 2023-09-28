from sqlalchemy import exc
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

from models import Category, CategoryGroup, Group
from enums import GroupStatusEnum
from schemas import CategoryModel, CategoryCreate, IconColor


def validate_input_data(
    db: Session,
    user_id: int,
    group_id: int,
) -> None:
    try:
        group = db.query(Group).filter_by(id=group_id, admin_id=user_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not admin of this group!",
        )
    if group.status == GroupStatusEnum.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Group is not active!",
        )


def create_category(
    db: Session, user_id: int, group_id: int, category: CategoryCreate
) -> CategoryModel:
    validate_input_data(db, user_id, group_id)
    db_category = (
        db.query(Category).filter_by(title=category.title.lower()).one_or_none()
    )
    if db_category is None:
        db_category = Category(title=category.title.lower())
        db.add(db_category)
        db.flush()
    else:
        db_category_group = (
            db.query(CategoryGroup)
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
    db_category_group = CategoryGroup(
        category_id=db_category.id,
        group_id=group_id,
        icon_url=category.icon_url,
        color_code=category.color_code,
    )
    db.add(db_category_group)
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while create category",
        )
    else:
        return db_category


def update_category(
    db: Session, user_id: int, group_id: int, icon_color: IconColor, category_id: int
) -> CategoryModel:
    validate_input_data(db, user_id, group_id)
    try:
        (
            db.query(CategoryGroup)
            .filter_by(
                group_id=group_id,
                category_id=category_id,
            )
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You do not have this category!",
        )
    db.query(CategoryGroup).filter_by(
        group_id=group_id,
        category_id=category_id,
    ).update(values={**icon_color.dict()})
    db_category_group = (
        db.query(Category)
        .filter_by(
            id=category_id,
        )
        .one()
    )
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while update category",
        )
    else:
        return db_category_group
