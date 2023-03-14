import datetime
from typing import List

from sqlalchemy import and_, exc
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

import schemas
from models import Invitation, ResponseStatus, UserGroup, User, Group, Status
from services import add_user_in_group


def response_invitation(
    db: Session, response: str, invitation_id: int, user_id: int
) -> schemas.Invitation:
    try:
        invitation = (
            db.query(Invitation)
            .filter(
                and_(
                    Invitation.recipient_id == user_id,
                    Invitation.status == ResponseStatus.PENDING,
                    Invitation.id == invitation_id,
                )
            )
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation is not found",
        )
    invitation.status = response
    db.commit()
    if response == ResponseStatus.ACCEPTED:
        add_user_in_group(db, invitation.group_id, user_id)
    return invitation


def read_invitations(db: Session, user_id: int) -> List[schemas.BaseInvitation]:
    overdue_invitations = (
        db.query(Invitation)
        .filter(
            and_(
                Invitation.recipient_id == user_id,
                Invitation.status == ResponseStatus.PENDING,
                Invitation.creation_time + datetime.timedelta(days=1)
                < datetime.datetime.now(),
            )
        )
        .all()
    )
    for invitation in overdue_invitations:
        invitation.status = ResponseStatus.OVERDUE
        db.commit()
    invitations = (
        db.query(Invitation)
        .filter(
            and_(
                Invitation.recipient_id == user_id,
                Invitation.status == ResponseStatus.PENDING,
            )
        )
        .all()
    )
    return invitations


def create_invitation(
    db: Session, data: schemas.CreateInvitation, user_id: int
) -> schemas.Invitation:
    try:
        group = (
            db.query(Group)
            .filter(and_(Group.admin_id == user_id, Group.id == data.group_id))
            .one()
        )
    except exc.NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not admin in this group!",
        )
    if group.status == Status.INACTIVE:
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
    user = (
        db.query(UserGroup)
        .filter(
            and_(
                UserGroup.user_id == data.recipient_id,
                UserGroup.group_id == data.group_id,
            )
        )
        .one_or_none()
    )
    if user:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The recipient is already in this group!",
        )
    invitation = (
        db.query(Invitation)
        .filter(
            and_(
                Invitation.status == ResponseStatus.PENDING,
                Invitation.recipient_id == data.recipient_id,
                Invitation.group_id == data.group_id,
            )
        )
        .one_or_none()
    )
    if invitation:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="The invitation has already been sent. Wait for a reply!",
        )
    db_invitation = Invitation(
        status=ResponseStatus.PENDING,
        sender_id=user_id,
        recipient_id=data.recipient_id,
        group_id=data.group_id,
        creation_time=datetime.datetime.utcnow(),
    )
    db.add(db_invitation)
    db.commit()
    db.refresh(db_invitation)
    return db_invitation
