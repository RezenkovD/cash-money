from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from starlette.status import HTTP_204_NO_CONTENT

import services
from database import get_db
from dependencies import (
    get_current_user,
    transform_date_or_422,
    transform_exact_date_or_422,
    Page,
)
from models import User
from schemas import (
    ReplenishmentCreate,
    ReplenishmentUpdate,
    ReplenishmentModel,
    UserReplenishment,
)

router = APIRouter(
    prefix="/replenishments",
    tags=["replenishments"],
)


@router.post("/", response_model=ReplenishmentModel)
def create_replenishment(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    replenishment: ReplenishmentCreate,
) -> ReplenishmentModel:
    return services.create_replenishment(db, current_user.id, replenishment)


@router.put("/{replenishment_id}/", response_model=ReplenishmentModel)
def update_replenishment(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    replenishment: ReplenishmentUpdate,
    replenishment_id: int,
) -> ReplenishmentModel:
    return services.update_replenishment(
        db, current_user.id, replenishment, replenishment_id
    )


@router.delete("/{replenishment_id}/", status_code=HTTP_204_NO_CONTENT)
def delete_replenishment(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    replenishment_id: int,
) -> None:
    services.delete_replenishment(db, current_user.id, replenishment_id)


@router.get("/", response_model=Page[UserReplenishment])
def read_replenishments(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year_month: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Page[UserReplenishment]:
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
        return paginate(
            db,
            services.read_replenishments(
                user_id=current_user.id, filter_date=filter_date
            ),
        )
    elif start_date and end_date:
        start_date = transform_exact_date_or_422(start_date)
        end_date = transform_exact_date_or_422(end_date)
        return paginate(
            db,
            services.read_replenishments(
                user_id=current_user.id,
                start_date=start_date,
                end_date=end_date,
            ),
        )
    else:
        return paginate(db, services.read_replenishments(user_id=current_user.id))
