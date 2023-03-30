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
    tags=["invitations"],
)


@router.post("/", response_model=schemas.Invitation)
def create_invitation(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    data: schemas.CreateInvitation,
) -> schemas.Invitation:
    return services.create_invitation(db, current_user.id, data)


@router.get("/list/", response_model=List[schemas.BaseInvitation])
def read_invitation(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> List[schemas.BaseInvitation]:
    return services.read_invitations(db, current_user.id)


@router.post("/response/{invitation_id}/", response_model=schemas.Invitation)
def response_invitation(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    invitation_id: int,
    response: models.UserResponse,
) -> schemas.Invitation:
    return services.response_invitation(db, current_user.id, invitation_id, response)
