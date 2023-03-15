import datetime
from operator import and_

import pytest
from starlette.exceptions import HTTPException

import models
from models import UserGroup, Status
from schemas import CreateGroup
from services import (
    create_group,
    add_user_in_group,
    read_users_group,
    read_user_groups,
    leave_group,
    remove_user,
    disband_group,
)
from tests.factories import UserFactory, GroupFactory


def test_create_group(session) -> None:
    user = UserFactory()
    user_data = {
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "picture": user.picture,
    }
    group = CreateGroup(title="test_title", description="test_description")
    db_data = create_group(session, group, user.id)
    assert db_data.title == "test_title"
    assert db_data.description == "test_description"
    assert db_data.status == Status.ACTIVE
    assert db_data.admin.login == user_data["login"]
    assert db_data.admin.first_name == user_data["first_name"]
    assert db_data.admin.last_name == user_data["last_name"]
    assert db_data.admin.picture == user_data["picture"]


def test_add_user_in_group(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    db_data = (
        session.query(UserGroup)
        .filter(and_(UserGroup.group_id == group.id, UserGroup.user_id == user.id))
        .one_or_none()
    )
    assert db_data is None
    add_user_in_group(session, group.id, user.id)
    db_data = (
        session.query(UserGroup)
        .filter(and_(UserGroup.group_id == group.id, UserGroup.user_id == user.id))
        .one_or_none()
    )
    assert db_data.user_id == user.id
    assert db_data.status == Status.ACTIVE
    assert db_data.group_id == group.id
    assert db_data.date_join.strftime("%Y-%m-%d") == datetime.date.today().strftime(
        "%Y-%m-%d"
    )


def test_read_users_group(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    add_user_in_group(session, group.id, first_user.id)
    add_user_in_group(session, group.id, second_user.id)
    db_data = read_users_group(session, group.id, first_user.id)
    users = [first_user, second_user]
    for data, user in zip(db_data.users_group, users):
        assert data.user.login == user.login
        assert data.status == Status.ACTIVE
        assert data.date_join.strftime("%Y-%m-%d") == datetime.date.today().strftime(
            "%Y-%m-%d"
        )


def test_read_user_groups(session) -> None:
    first_user = UserFactory()
    first_group = GroupFactory(admin_id=first_user.id)
    second_group = GroupFactory(admin_id=first_user.id)
    db_data = read_user_groups(session, first_user.id)
    assert db_data.user_groups == []
    add_user_in_group(session, first_group.id, first_user.id)
    add_user_in_group(session, second_group.id, first_user.id)
    db_data = read_user_groups(session, first_user.id)
    groups = [first_group, second_group]
    for data, group in zip(db_data.user_groups, groups):
        assert data.group.title == group.title
        assert data.group.status == Status.ACTIVE


def test_leave_group_user(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    add_user_in_group(session, group.id, first_user.id)
    add_user_in_group(session, group.id, second_user.id)
    users = read_users_group(session, group.id, first_user.id)
    for user in users.users_group:
        assert user.status == Status.ACTIVE
    data = leave_group(session, group.id, second_user.id)
    assert data.user.id == second_user.id
    assert data.status == Status.INACTIVE

    with pytest.raises(HTTPException) as ex_info:
        leave_group(session, 9999, second_user.id)
    assert "Group is not found" in str(ex_info.value.detail)


def test_leave_group_admin(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    assert group.status == Status.ACTIVE
    add_user_in_group(session, group.id, first_user.id)
    add_user_in_group(session, group.id, second_user.id)
    db_users = read_users_group(session, group.id, first_user.id)
    for user in db_users.users_group:
        assert user.status == Status.ACTIVE
    leave_group(session, group.id, first_user.id)
    db_users = read_users_group(session, group.id, first_user.id)
    for user in db_users.users_group:
        assert user.status == Status.INACTIVE
    db_group = session.query(models.Group).filter_by(id=group.id).one()
    assert db_group.status == Status.INACTIVE


def test_disband_group(session):
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    add_user_in_group(session, group.id, first_user.id)
    add_user_in_group(session, group.id, second_user.id)
    data = disband_group(session, group.id)
    for user in data.users_group:
        assert user.status == Status.INACTIVE
    db_group = session.query(models.Group).filter_by(id=group.id).one()
    assert db_group.status == Status.INACTIVE


def test_remove_user(session):
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    add_user_in_group(session, group.id, first_user.id)
    add_user_in_group(session, group.id, second_user.id)
    users = read_users_group(session, group.id, first_user.id)
    for user in users.users_group:
        assert user.status == Status.ACTIVE

    with pytest.raises(HTTPException) as ex_info:
        remove_user(session, group.id, first_user.id, second_user.id)
    assert "You are not admin in this group!" in str(ex_info.value.detail)

    data = remove_user(session, group.id, second_user.id, first_user.id)
    assert data.user.id == second_user.id
    assert data.status == Status.INACTIVE

    with pytest.raises(HTTPException) as ex_info:
        remove_user(session, group.id, second_user.id, first_user.id)
    assert "The user is not active or does not exist in this group!" in str(ex_info.value.detail)

    db_group = session.query(models.Group).filter_by(id=group.id).one()
    assert db_group.status == Status.ACTIVE
    data = remove_user(session, group.id, first_user.id, first_user.id)
    for user in data.users_group:
        assert user.status == Status.INACTIVE
    db_group = session.query(models.Group).filter_by(id=group.id).one()
    assert db_group.status == Status.INACTIVE
