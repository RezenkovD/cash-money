from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter

from database import get_db
from dependencies import get_current_user
from models import UserResponse, User
from schemas import Invitation, BaseInvitation, CreateInvitation
import services

router = APIRouter(
    prefix="/invitations",
    tags=["invitations"],
)


@router.post("/", response_model=Invitation)
def create_invitation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: CreateInvitation,
) -> Invitation:
    return services.create_invitation(db, current_user.id, data)


@router.get("/list/", response_model=List[BaseInvitation])
def read_invitation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[BaseInvitation]:
    return services.read_invitations(db, current_user.id)


@router.post("/response/{invitation_id}/", response_model=Invitation)
def response_invitation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    invitation_id: int,
    response: UserResponse,
) -> Invitation:
    return services.response_invitation(db, current_user.id, invitation_id, response)
