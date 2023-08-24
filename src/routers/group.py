from typing import Union, Optional, List

from fastapi import APIRouter, Depends
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

import services
from database import get_db
from dependencies import get_current_user
from models import User
from schemas import (
    AboutUser,
    GroupCreate,
    GroupModel,
    UsersGroup,
    UserGroups,
    GroupInfo,
    GroupHistory,
    GroupTotalExpenses,
    GroupUserTotalExpenses,
    UserSpender,
)
from dependencies import Page, transform_date_or_422, transform_exact_date_or_422

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


@router.get("/", response_model=UserGroups)
def read_user_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserGroups:
    return services.read_user_groups(db, current_user.id)


@router.post("/", response_model=GroupModel)
def create_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group: GroupCreate,
) -> GroupModel:
    return services.create_group(db, current_user.id, group)


@router.put("/{group_id}/", response_model=GroupModel)
def update_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group: GroupCreate,
    group_id: int,
) -> GroupModel:
    return services.update_group(db, current_user.id, group, group_id)


@router.get("/{group_id}/users/", response_model=UsersGroup)
def read_users_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
) -> UsersGroup:
    return services.read_users_group(db, current_user.id, group_id)


@router.post("/{group_id}/leave/", response_model=Union[AboutUser, UsersGroup])
def leave_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
) -> Union[AboutUser, UsersGroup]:
    return services.leave_group(db, current_user.id, group_id)


@router.post(
    "/{group_id}/users/{user_id}/remove/",
    response_model=Union[AboutUser, UsersGroup],
)
def remove_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    user_id: int,
) -> Union[AboutUser, UsersGroup]:
    return services.remove_user(db, current_user.id, group_id, user_id)


@router.get("/{group_id}/history/", response_model=Page[GroupHistory])
def read_user_history(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
) -> Page[GroupHistory]:
    return paginate(db, services.group_history(db, current_user.id, group_id))


@router.get("/{group_id}/info/", response_model=GroupInfo)
def read_group_info(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
) -> GroupInfo:
    return services.read_group_info(db, current_user.id, group_id)


@router.get("/{group_id}/total-expenses/", response_model=GroupTotalExpenses)
def read_group_total_expenses(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    year_month: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> GroupTotalExpenses:
    if year_month and (start_date or end_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot use filter_date with start_date or end_date",
        )
    elif (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Both start_date and end_date are required",
        )
    elif year_month:
        filter_date = transform_date_or_422(year_month)
        return services.group_total_expenses(
            db, current_user.id, group_id, filter_date=filter_date
        )
    elif start_date and end_date:
        start_date = transform_exact_date_or_422(start_date)
        end_date = transform_exact_date_or_422(end_date)
        return services.group_total_expenses(
            db, current_user.id, group_id, start_date=start_date, end_date=end_date
        )
    else:
        return services.group_total_expenses(db, current_user.id, group_id)


@router.get("/{group_id}/my-total-expenses/", response_model=GroupUserTotalExpenses)
def read_group_user_total_expenses(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    year_month: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> GroupUserTotalExpenses:
    if year_month and (start_date or end_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot use filter_date with start_date or end_date",
        )
    elif (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Both start_date and end_date are required",
        )
    elif year_month:
        filter_date = transform_date_or_422(year_month)
        return services.group_user_total_expenses(
            db, current_user.id, group_id, filter_date=filter_date
        )
    elif start_date and end_date:
        start_date = transform_exact_date_or_422(start_date)
        end_date = transform_exact_date_or_422(end_date)
        return services.group_user_total_expenses(
            db, current_user.id, group_id, start_date=start_date, end_date=end_date
        )
    else:
        return services.group_user_total_expenses(db, current_user.id, group_id)


@router.get("/{group_id}/users-spenders/", response_model=List[UserSpender])
def read_group_users_spenders(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int,
    year_month: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[UserSpender]:
    if year_month and (start_date or end_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot use filter_date with start_date or end_date",
        )
    elif (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Both start_date and end_date are required",
        )
    elif year_month:
        filter_date = transform_date_or_422(year_month)
        return services.group_users_spenders(
            db, current_user.id, group_id, filter_date=filter_date
        )
    elif start_date and end_date:
        start_date = transform_exact_date_or_422(start_date)
        end_date = transform_exact_date_or_422(end_date)
        return services.group_users_spenders(
            db, current_user.id, group_id, start_date=start_date, end_date=end_date
        )
    else:
        return services.group_users_spenders(db, current_user.id, group_id)
