import datetime
from dateutil.relativedelta import relativedelta
from typing import Union, List, Optional

from sqlalchemy import exc, func, select, desc, and_, extract
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.functions import coalesce, sum
from starlette import status
from starlette.exceptions import HTTPException
from pydantic.schema import date

from models import Group, User, UserGroup, Expense, CategoryGroup, Category
from enums import GroupStatusEnum
from schemas import (
    AboutUser,
    CategoriesGroup,
    GroupCreate,
    GroupModel,
    UserGroups,
    UsersGroup,
    GroupInfo,
    GroupHistory,
    GroupTotalExpenses,
    GroupUserTotalExpenses,
    CategoryExpenses,
)


def group_history(db: Session, user_id: int, group_id: int) -> List[GroupHistory]:
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
    history = (
        select(
            Expense.id,
            Expense.descriptions,
            Expense.amount,
            Expense.time,
            Expense.category_id,
            CategoryGroup.color_code.label("color_code_category"),
            Category.title.label("title_category"),
            User.id.label("user_id"),
            User.login.label("user_login"),
            User.first_name.label("user_first_name"),
            User.last_name.label("user_last_name"),
            User.picture.label("user_picture"),
        )
        .join(CategoryGroup, Expense.category_id == CategoryGroup.category_id)
        .join(Category, CategoryGroup.category_id == Category.id)
        .join(User, User.id == Expense.user_id)
        .filter(Expense.group_id == group_id)
        .order_by(desc(Expense.time))
    )
    return history


def read_group_info(db: Session, user_id: int, group_id: int) -> GroupInfo:
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
    group = (
        db.query(Group).options(joinedload(Group.admin)).filter_by(id=group_id).one()
    )
    group_users_count = (
        db.query(func.count(UserGroup.user_id)).filter_by(group_id=group_id).scalar()
    )
    group_expenses_count = (
        db.query(func.count(Expense.id)).filter_by(group_id=group_id).scalar()
    )
    group_info = GroupInfo(
        id=group.id,
        title=group.title,
        description=group.description,
        status=group.status,
        icon_url=group.icon_url,
        color_code=group.color_code,
        admin=group.admin,
        members=group_users_count,
        expenses=group_expenses_count,
    )
    return group_info


def remove_user(
    db: Session, admin_id: int, group_id: int, user_id: int
) -> Union[AboutUser, UsersGroup]:
    try:
        db.query(Group).filter_by(id=group_id, admin_id=admin_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not admin in this group!",
        )
    try:
        (
            db.query(UserGroup)
            .filter_by(
                user_id=user_id,
                group_id=group_id,
                status=GroupStatusEnum.ACTIVE,
            )
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The user is not active or does not exist in this group!",
        )
    if admin_id == user_id:
        try:
            db_users_group = disband_group(db, group_id)
            db.commit()
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"An error occurred while disband group",
            )
        else:
            return db_users_group
    else:
        try:
            db_user_group = leave_group(db, user_id, group_id)
            db.commit()
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"An error occurred while remove user",
            )
        else:
            return db_user_group


def disband_group(db: Session, group_id: int) -> UsersGroup:
    db_group = db.query(Group).filter_by(id=group_id).one()
    db_group.status = GroupStatusEnum.INACTIVE
    db.query(UserGroup).filter_by(group_id=group_id).update(
        {UserGroup.status: GroupStatusEnum.INACTIVE}
    )
    db_users_group = (
        db.query(Group)
        .options(joinedload(Group.users_group))
        .filter_by(id=group_id)
        .one()
    )
    return db_users_group


def leave_group(
    db: Session, user_id: int, group_id: int
) -> Union[AboutUser, UsersGroup]:
    db_admin_group = (
        db.query(Group).filter_by(id=group_id, admin_id=user_id).one_or_none()
    )
    if db_admin_group:
        try:
            db_users_group = disband_group(db, group_id)
            db.commit()
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"An error occurred while leave group",
            )
        else:
            return db_users_group
    try:
        db_user_group = (
            db.query(UserGroup)
            .filter_by(
                group_id=group_id,
                user_id=user_id,
            )
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group is not found",
        )
    db_user_group.status = GroupStatusEnum.INACTIVE
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while leave group",
        )
    else:
        return db_user_group


def create_group(db: Session, user_id: int, group: GroupCreate) -> GroupModel:
    db_group = Group(
        **group.dict(),
        admin_id=user_id,
        status=GroupStatusEnum.ACTIVE,
    )
    db.add(db_group)
    try:
        db.flush()
        add_user_in_group(db, user_id, db_group.id)
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while create group",
        )
    else:
        return db_group


def update_group(
    db: Session, user_id: int, group: GroupCreate, group_id: int
) -> GroupModel:
    try:
        db.query(Group).filter_by(id=group_id, admin_id=user_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not an admin of this group!",
        )
    db.query(Group).filter_by(id=group_id).update(values={**group.dict()})
    db_group = db.query(Group).filter_by(id=group_id).one()
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while update group",
        )
    else:
        return db_group


def add_user_in_group(db: Session, user_id: int, group_id: int) -> None:
    db_user_group = (
        db.query(UserGroup)
        .filter_by(
            user_id=user_id,
            group_id=group_id,
            status=GroupStatusEnum.INACTIVE,
        )
        .one_or_none()
    )
    if db_user_group:
        db_user_group.status = GroupStatusEnum.ACTIVE
    else:
        db_user_group = UserGroup(
            user_id=user_id,
            group_id=group_id,
            date_join=datetime.date.today(),
            status=GroupStatusEnum.ACTIVE,
        )
        db.add(db_user_group)


def read_users_group(db: Session, user_id: int, group_id: int) -> UsersGroup:
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
    db_query = (
        db.query(Group)
        .options(joinedload(Group.users_group))
        .filter_by(id=group_id)
        .one()
    )
    return db_query


def read_user_groups(db: Session, user_id: int) -> UserGroups:
    db_query = (
        db.query(User).options(joinedload(User.user_groups)).filter_by(id=user_id).one()
    )
    return db_query


def read_categories_group(db: Session, user_id: int, group_id: int) -> CategoriesGroup:
    try:
        db.query(UserGroup).filter_by(
            group_id=group_id,
            user_id=user_id,
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You are not a user of this group!",
        )
    db_query = (
        db.query(Group)
        .options(joinedload(Group.categories_group))
        .filter_by(id=group_id)
        .one()
    )
    return db_query


def get_group_expenses_for_month(
    db: Session,
    group_id: int,
    year: date,
    month: date,
) -> float:
    return db.query(
        coalesce(
            sum(Expense.amount).filter(
                and_(
                    Expense.group_id == group_id,
                    extract("year", Expense.time) == year,
                    extract("month", Expense.time) == month,
                )
            ),
            0,
        )
    ).one()[0]


def get_group_expenses_for_time_range(
    db: Session,
    group_id: int,
    start_date: date,
    end_date: date,
) -> float:
    return db.query(
        coalesce(
            sum(Expense.amount).filter(
                and_(
                    Expense.group_id == group_id,
                    Expense.time >= start_date,
                    Expense.time <= end_date,
                )
            ),
            0,
        )
    ).one()[0]


def group_total_expenses(
    db: Session,
    user_id: int,
    group_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> GroupTotalExpenses:
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
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    (amount,) = db.query(
        coalesce(sum(Expense.amount).filter(Expense.group_id == group_id), 0)
    ).one()
    percentage_increase = 0

    if filter_date:
        year, month = filter_date.year, filter_date.month
        amount = get_group_expenses_for_month(db, group_id, year, month)

        filter_date = filter_date - relativedelta(months=1)
        previous_year, previous_month = filter_date.year, filter_date.month
        previous_month_amount = get_group_expenses_for_month(
            db, group_id, previous_year, previous_month
        )

        if previous_month_amount != 0:
            percentage_increase = (
                amount - previous_month_amount
            ) / previous_month_amount

    elif start_date and end_date:
        amount = get_group_expenses_for_time_range(db, group_id, start_date, end_date)

        days_difference = (end_date - start_date).days
        zero_date = start_date - relativedelta(days=days_difference)
        previous_days_amount = get_group_expenses_for_time_range(
            db, group_id, zero_date, start_date
        )

        if previous_days_amount != 0:
            percentage_increase = (amount - previous_days_amount) / previous_days_amount

    total_expenses = GroupTotalExpenses(
        amount=amount, percentage_increase=percentage_increase
    )
    return total_expenses


def get_group_user_expenses_for_month(
    db: Session,
    user_id: int,
    group_id: int,
    year: date,
    month: date,
) -> float:
    return db.query(
        coalesce(
            sum(Expense.amount).filter(
                and_(
                    Expense.user_id == user_id,
                    Expense.group_id == group_id,
                    extract("year", Expense.time) == year,
                    extract("month", Expense.time) == month,
                )
            ),
            0,
        )
    ).one()[0]


def get_group_user_expenses_for_time_range(
    db: Session,
    user_id: int,
    group_id: int,
    start_date: date,
    end_date: date,
) -> float:
    return db.query(
        coalesce(
            sum(Expense.amount).filter(
                and_(
                    Expense.user_id == user_id,
                    Expense.group_id == group_id,
                    Expense.time >= start_date,
                    Expense.time <= end_date,
                )
            ),
            0,
        )
    ).one()[0]


def group_user_total_expenses(
    db: Session,
    user_id: int,
    group_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> GroupTotalExpenses:
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
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    (amount,) = db.query(
        coalesce(
            sum(Expense.amount).filter(
                and_(Expense.group_id == group_id, Expense.user_id == user_id)
            ),
            0,
        )
    ).one()
    percentage_increase = 0

    if filter_date:
        year, month = filter_date.year, filter_date.month
        amount = get_group_user_expenses_for_month(db, user_id, group_id, year, month)

        filter_date = filter_date - relativedelta(months=1)
        previous_year, previous_month = filter_date.year, filter_date.month
        previous_month_amount = get_group_user_expenses_for_month(
            db, user_id, group_id, previous_year, previous_month
        )

        if previous_month_amount != 0:
            percentage_increase = (
                amount - previous_month_amount
            ) / previous_month_amount

    elif start_date and end_date:
        amount = get_group_user_expenses_for_time_range(
            db, user_id, group_id, start_date, end_date
        )

        days_difference = (end_date - start_date).days
        zero_date = start_date - relativedelta(days=days_difference)
        previous_days_amount = get_group_user_expenses_for_time_range(
            db, user_id, group_id, zero_date, start_date
        )

        if previous_days_amount != 0:
            percentage_increase = (amount - previous_days_amount) / previous_days_amount

    total_expenses = GroupUserTotalExpenses(
        amount=amount, percentage_increase=percentage_increase
    )
    return total_expenses


def group_users_spenders(
    db: Session,
    user_id: int,
    group_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[GroupTotalExpenses]:
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
    if filter_date and start_date or filter_date and end_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Too many arguments! It is necessary to select either a month or a start date and an end date!",
        )
    users_spenders = (
        db.query(
            User.id.label("id"),
            User.first_name.label("first_name"),
            User.last_name.label("last_name"),
            User.picture.label("picture"),
            func.coalesce(func.sum(Expense.amount), 0).label("amount"),
        )
        .join(UserGroup, User.id == UserGroup.user_id)
        .outerjoin(
            Expense,
            and_(
                Expense.user_id == User.id,
                Expense.group_id == group_id,
            ),
        )
        .filter(UserGroup.group_id == group_id)
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(Expense.amount), 0).desc())
        .all()
    )
    if filter_date:
        users_spenders = (
            db.query(
                User.id.label("id"),
                User.first_name.label("first_name"),
                User.last_name.label("last_name"),
                User.picture.label("picture"),
                func.coalesce(func.sum(Expense.amount), 0).label("amount"),
            )
            .join(UserGroup, User.id == UserGroup.user_id)
            .outerjoin(
                Expense,
                and_(
                    Expense.user_id == User.id,
                    Expense.group_id == group_id,
                    extract("year", Expense.time) == filter_date.year,
                    extract("month", Expense.time) == filter_date.month,
                ),
            )
            .filter(UserGroup.group_id == group_id)
            .group_by(User.id)
            .order_by(func.coalesce(func.sum(Expense.amount), 0).desc())
            .all()
        )
    elif start_date and end_date:
        users_spenders = (
            db.query(
                User.id.label("id"),
                User.first_name.label("first_name"),
                User.last_name.label("last_name"),
                User.picture.label("picture"),
                func.coalesce(func.sum(Expense.amount), 0).label("amount"),
            )
            .join(UserGroup, User.id == UserGroup.user_id)
            .outerjoin(
                Expense,
                and_(
                    Expense.user_id == User.id,
                    Expense.group_id == group_id,
                    Expense.time >= start_date,
                    Expense.time <= end_date,
                ),
            )
            .filter(UserGroup.group_id == group_id)
            .group_by(User.id)
            .order_by(func.coalesce(func.sum(Expense.amount), 0).desc())
            .all()
        )
    return users_spenders


def group_category_expenses(
    db: Session,
    user_id: int,
    group_id: int,
    filter_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[CategoryExpenses]:
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
    categories_expenses_subquery = (
        db.query(
            Expense.category_id.label("id"),
            func.coalesce(func.sum(Expense.amount), 0).label("amount"),
        )
        .filter(
            Expense.group_id == group_id,
        )
        .group_by(Expense.category_id)
        .subquery()
    )
    if filter_date:
        categories_expenses_subquery = (
            db.query(
                Expense.category_id.label("id"),
                func.coalesce(func.sum(Expense.amount), 0).label("amount"),
            )
            .filter(
                and_(
                    Expense.group_id == group_id,
                    extract("year", Expense.time) == filter_date.year,
                    extract("month", Expense.time) == filter_date.month,
                )
            )
            .group_by(Expense.category_id)
            .subquery()
        )
    elif start_date and end_date:
        categories_expenses_subquery = (
            db.query(
                Expense.category_id.label("id"),
                func.coalesce(func.sum(Expense.amount), 0).label("amount"),
            )
            .filter(
                and_(
                    Expense.group_id == group_id,
                    Expense.time >= start_date,
                    Expense.time <= end_date,
                ),
            )
            .group_by(Expense.category_id)
            .subquery()
        )
    categories_expenses = (
        db.query(
            Category.id.label("id"),
            Category.title.label("title"),
            CategoryGroup.color_code.label("color_code"),
            CategoryGroup.icon_url.label("icon_url"),
            categories_expenses_subquery.c.amount,
        )
        .join(
            CategoryGroup,
            and_(
                CategoryGroup.category_id == Category.id,
                CategoryGroup.group_id == group_id,
            ),
        )
        .outerjoin(
            categories_expenses_subquery,
            Category.id == categories_expenses_subquery.c.id,
        )
        .order_by(desc(categories_expenses_subquery.c.amount))
        .all()
    )
    return categories_expenses
