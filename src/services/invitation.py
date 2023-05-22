import datetime
from typing import List

from sqlalchemy import and_, exc
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

from models import (
    Group,
    Invitation,
    User,
    UserGroup,
)
from enums import GroupStatusEnum, ResponseStatusEnum, UserResponseEnum
from schemas import BaseInvitation, InvitationCreate, InvitationModel
from services import add_user_in_group


def update_invitation_info(db: Session, user_id: int) -> None:
    db.query(Invitation).filter(
        and_(
            Invitation.recipient_id == user_id,
            Invitation.status == ResponseStatusEnum.PENDING,
            Invitation.creation_time + datetime.timedelta(hours=24)
            < datetime.datetime.utcnow(),
        )
    ).update({Invitation.status: ResponseStatusEnum.OVERDUE})
    groups = db.query(Group.id).filter_by(status=GroupStatusEnum.INACTIVE)
    db.query(Invitation).filter(
        and_(
            Invitation.recipient_id == user_id,
            Invitation.status == ResponseStatusEnum.PENDING,
            Invitation.group_id.in_(groups),
        )
    ).update({Invitation.status: ResponseStatusEnum.OVERDUE})


def response_invitation(
    db: Session, user_id: int, invitation_id: int, response: UserResponseEnum
) -> InvitationModel:
    update_invitation_info(db, user_id)
    try:
        db_invitation = (
            db.query(Invitation)
            .filter_by(
                recipient_id=user_id,
                status=ResponseStatusEnum.PENDING,
                id=invitation_id,
            )
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation is not found",
        )
    db_invitation.status = response
    if response == ResponseStatusEnum.ACCEPTED:
        try:
            add_user_in_group(db, user_id, db_invitation.group_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"An error occurred while add user in group",
            )
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while response invitation",
        )
    else:
        return db_invitation


def read_invitations(db: Session, user_id: int) -> List[BaseInvitation]:
    update_invitation_info(db, user_id)
    db_invitations = (
        db.query(Invitation)
        .filter_by(
            recipient_id=user_id,
            status=ResponseStatusEnum.PENDING,
        )
        .all()
    )
    return db_invitations


def create_invitation(
    db: Session, user_id: int, data: InvitationCreate
) -> InvitationModel:
    try:
        db_group = db.query(Group).filter_by(admin_id=user_id, id=data.group_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not admin in this group!",
        )
    if db_group.status == GroupStatusEnum.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The group is inactive",
        )
    try:
        db.query(User).filter_by(id=data.recipient_id).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not found!",
        )
    db_user = (
        db.query(UserGroup)
        .filter_by(
            user_id=data.recipient_id,
            group_id=data.group_id,
            status=GroupStatusEnum.ACTIVE,
        )
        .one_or_none()
    )
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The recipient is already in this group!",
        )
    db_invitation = (
        db.query(Invitation)
        .filter_by(
            status=ResponseStatusEnum.PENDING,
            recipient_id=data.recipient_id,
            group_id=data.group_id,
        )
        .one_or_none()
    )
    if db_invitation:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The invitation has already been sent. Wait for a reply!",
        )
    db_invitation = Invitation(
        status=ResponseStatusEnum.PENDING,
        sender_id=user_id,
        recipient_id=data.recipient_id,
        group_id=data.group_id,
        creation_time=datetime.datetime.utcnow(),
    )
    db.add(db_invitation)
    try:
        db.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"An error occurred while create invitation",
        )
    else:
        return db_invitation
