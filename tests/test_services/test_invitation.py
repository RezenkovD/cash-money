import datetime

import pytest
from starlette.exceptions import HTTPException

from models import ResponseStatusEnum, GroupStatusEnum
from schemas import CreateInvitation
from services import (
    create_invitation,
    read_invitations,
    response_invitation,
    read_users_group,
    leave_group,
)
from tests.factories import (
    UserFactory,
    GroupFactory,
    UserGroupFactory,
    InvitationFactory,
)


def test_create_invitation(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    data = CreateInvitation(recipient_id=second_user.id, group_id=group.id)
    invitation = create_invitation(session, first_user.id, data)
    assert invitation.status == ResponseStatusEnum.PENDING
    assert invitation.recipient.id == second_user.id
    assert invitation.group.id == group.id
    assert invitation.group.admin.id == first_user.id


def test_create_invitation_as_non_admin(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    data = CreateInvitation(recipient_id=second_user.id, group_id=9999)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, first_user.id, data)
    assert "You are not admin in this group!" in str(ex_info.value.detail)


def test_create_invitation_to_inactive_group(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id, status=GroupStatusEnum.INACTIVE)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    data = CreateInvitation(recipient_id=second_user.id, group_id=group.id)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, first_user.id, data)
    assert "The group is inactive" in str(ex_info.value.detail)


def test_create_invitation_to_nonexistent_user(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    data = CreateInvitation(recipient_id=9999, group_id=group.id)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, user.id, data)
    assert "User is not found!" in str(ex_info.value.detail)


def test_create_invitation_to_group_user(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    UserGroupFactory(user_id=second_user.id, group_id=group.id)
    data = CreateInvitation(recipient_id=second_user.id, group_id=group.id)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, first_user.id, data)
    assert "The recipient is already in this group!" in str(ex_info.value.detail)


def test_create_invitation_twice(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    data = CreateInvitation(recipient_id=second_user.id, group_id=group.id)
    create_invitation(session, first_user.id, data)
    with pytest.raises(HTTPException) as ex_info:
        create_invitation(session, first_user.id, data)
    assert "The invitation has already been sent. Wait for a reply!" in str(
        ex_info.value.detail
    )


def test_read_invitations(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    InvitationFactory(
        sender_id=first_user.id, recipient_id=second_user.id, group_id=group.id
    )
    invitations = read_invitations(session, second_user.id)
    groups = [group]
    assert len(invitations) == len(groups)
    for invitation, group in zip(invitations, groups):
        assert invitation.status == ResponseStatusEnum.PENDING
        assert invitation.group.id == group.id
        assert invitation.group.admin.id == group.admin_id
        assert invitation.creation_time.strftime(
            "%Y-%m-%d"
        ) == datetime.date.today().strftime("%Y-%m-%d")


def test_response_invitation(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)

    users_group = read_users_group(session, first_user.id, group.id).users_group

    assert len(users_group) == 1

    data = InvitationFactory(
        sender_id=first_user.id, recipient_id=second_user.id, group_id=group.id
    )
    invitation = response_invitation(
        session, second_user.id, data.id, ResponseStatusEnum.DENIED
    )
    assert invitation.id == data.id
    assert invitation.status == ResponseStatusEnum.DENIED
    assert invitation.group.id == group.id
    assert invitation.group.admin.id == first_user.id
    assert invitation.creation_time.strftime(
        "%Y-%m-%d"
    ) == datetime.date.today().strftime("%Y-%m-%d")
    assert invitation.recipient.id == second_user.id

    users_group = read_users_group(session, first_user.id, group.id).users_group
    users = [first_user]
    assert len(users_group) == len(users)
    for user_group, user in zip(users_group, users):
        assert user_group.user.id == user.id
        assert user_group.status == GroupStatusEnum.ACTIVE

    data = InvitationFactory(
        sender_id=first_user.id, recipient_id=second_user.id, group_id=group.id
    )
    invitation = response_invitation(
        session, second_user.id, data.id, ResponseStatusEnum.ACCEPTED
    )
    assert invitation.id == invitation.id
    assert invitation.status == ResponseStatusEnum.ACCEPTED
    assert invitation.group.id == group.id
    assert invitation.group.admin.id == first_user.id
    assert invitation.creation_time.strftime(
        "%Y-%m-%d"
    ) == datetime.date.today().strftime("%Y-%m-%d")
    assert invitation.recipient.id == second_user.id

    users.append(second_user)
    users_group = read_users_group(session, first_user.id, group.id).users_group
    assert len(users_group) == len(users)
    for user_group, user in zip(users_group, users):
        assert user_group.user.id == user.id
        assert user_group.status == GroupStatusEnum.ACTIVE


def test_response_invitation_not_found(session) -> None:
    user = UserFactory()
    with pytest.raises(HTTPException) as ex_info:
        response_invitation(session, user.id, 9999, ResponseStatusEnum.DENIED)
    assert "Invitation is not found" in str(ex_info.value.detail)


def test_response_invitation_in_inactive_group(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    invitation = InvitationFactory(
        sender_id=first_user.id,
        recipient_id=second_user.id,
        group_id=group.id,
    )
    leave_group(session, first_user.id, group.id)
    with pytest.raises(HTTPException) as ex_info:
        response_invitation(
            session, second_user.id, invitation.id, ResponseStatusEnum.ACCEPTED
        )
    assert "Invitation is not found" in str(ex_info.value.detail)
