from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import services
from database import get_db
from dependencies import get_current_user
from models import User
from enums import UserResponseEnum
from schemas import BaseInvitation, InvitationCreate, InvitationModel

router = APIRouter(
    prefix="/invitations",
    tags=["invitations"],
)


@router.post("/", response_model=InvitationModel)
def create_invitation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: InvitationCreate,
) -> InvitationModel:
    return services.create_invitation(db, current_user.id, data)


@router.get("/list/", response_model=List[BaseInvitation])
def read_invitation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[BaseInvitation]:
    return services.read_invitations(db, current_user.id)


@router.post("/response/{invitation_id}/", response_model=InvitationModel)
def response_invitation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    invitation_id: int,
    response: UserResponseEnum,
) -> InvitationModel:
    return services.response_invitation(db, current_user.id, invitation_id, response)
