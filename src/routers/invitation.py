from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database import get_db
from dependencies import get_current_user
import models
import schemas
import services


router = APIRouter(
    prefix="/invitations",
    tags=["invitation"],
)


@router.post("/", response_model=schemas.Invitation)
def create_invitation(
    data: schemas.CreateInvitation,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.Invitation:
    return services.create_invitation(db, data, current_user.id)


@router.get("/list/", response_model=List[schemas.BaseInvitation])
def read_invitation(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.BaseInvitation]:
    return services.read_invitations(db, current_user.id)


@router.post("/response/{invitation_id}", response_model=schemas.Invitation)
def response_invitation(
    response: models.UserResponse,
    invitation_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.Invitation:
    return services.response_invitation(db, response, invitation_id, current_user.id)
