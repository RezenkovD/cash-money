import datetime

import pytest
from starlette.exceptions import HTTPException

from models import ResponseStatus, Status
from schemas import CreateInvitation
from services import (
    add_user_in_group,
    create_invitation,
    read_invitations,
    response_invitation,
    read_users_group,
)
from tests.factories import UserFactory, GroupFactory


def test_create_invitation(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    add_user_in_group(session, group.id, first_user.id)
    data = CreateInvitation(recipient_id=first_user.id, group_id=group.id)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, data, second_user.id)
    assert "You are not admin in this group!" in str(ex_info.value.detail)

    data = CreateInvitation(recipient_id=second_user.id, group_id=group.id)
    db_invitation = create_invitation(session, data, first_user.id)
    assert db_invitation.status == ResponseStatus.PENDING
    assert db_invitation.recipient.id == second_user.id
    assert db_invitation.group.id == group.id
    assert db_invitation.group.admin.id == first_user.id

    data = CreateInvitation(recipient_id=second_user.id, group_id=9999)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, data, first_user.id)
    assert "You are not admin in this group!" in str(ex_info.value.detail)

    data = CreateInvitation(recipient_id=9999, group_id=group.id)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, data, first_user.id)
    assert "User is not found!" in str(ex_info.value.detail)

    data = CreateInvitation(recipient_id=second_user.id, group_id=group.id)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, data, first_user.id)
    assert "The invitation has already been sent. Wait for a reply!" in str(
        ex_info.value.detail
    )


def test_read_invitations(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    add_user_in_group(session, group.id, first_user.id)
    data = CreateInvitation(recipient_id=second_user.id, group_id=group.id)
    create_invitation(session, data, first_user.id)
    db_invitations = read_invitations(session, second_user.id)
    groups = [group]
    for invitation, group in zip(db_invitations, groups):
        assert invitation.status == ResponseStatus.PENDING
        assert invitation.group.id == group.id
        assert invitation.group.admin.id == group.admin_id
        assert invitation.creation_time.strftime(
            "%Y-%m-%d"
        ) == datetime.date.today().strftime("%Y-%m-%d")


def test_response_invitation(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    add_user_in_group(session, group.id, first_user.id)
    data = CreateInvitation(recipient_id=second_user.id, group_id=group.id)
    len_users_group = len(
        read_users_group(session, group.id, first_user.id).users_group
    )
    assert len_users_group == 1

    db_invitation = create_invitation(session, data, first_user.id)
    db_invitation = response_invitation(
        session, ResponseStatus.DENIED, db_invitation.id, second_user.id
    )
    assert db_invitation.id == db_invitation.id
    assert db_invitation.status == ResponseStatus.DENIED
    assert db_invitation.group.id == group.id
    assert db_invitation.group.admin.id == first_user.id
    assert db_invitation.creation_time.strftime(
        "%Y-%m-%d"
    ) == datetime.date.today().strftime("%Y-%m-%d")
    assert db_invitation.recipient.id == second_user.id

    db_users_group = read_users_group(session, group.id, first_user.id).users_group
    users = [first_user]
    for user_group, user in zip(db_users_group, users):
        assert user_group.user.id == user.id
        assert user_group.status == Status.ACTIVE

    db_invitation = create_invitation(session, data, first_user.id)
    db_invitation = response_invitation(
        session, ResponseStatus.ACCEPTED, db_invitation.id, second_user.id
    )
    assert db_invitation.id == db_invitation.id
    assert db_invitation.status == ResponseStatus.ACCEPTED
    assert db_invitation.group.id == group.id
    assert db_invitation.group.admin.id == first_user.id
    assert db_invitation.creation_time.strftime(
        "%Y-%m-%d"
    ) == datetime.date.today().strftime("%Y-%m-%d")
    assert db_invitation.recipient.id == second_user.id

    users.append(second_user)
    for user_group, user in zip(db_users_group, users):
        assert user_group.user.id == user.id
        assert user_group.status == Status.ACTIVE

    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, data, first_user.id)
    assert "The recipient is already in this group!" in str(ex_info.value.detail)

    group = GroupFactory(admin_id=first_user.id, status=Status.INACTIVE)
    add_user_in_group(session, group.id, first_user.id)
    data = CreateInvitation(recipient_id=second_user.id, group_id=group.id)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, data, first_user.id)
    assert "The group is inactive" in str(ex_info.value.detail)
