import datetime
import pytest
from operator import and_

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
    read_categories_group,
)
from tests.factories import (
    UserFactory,
    GroupFactory,
    CategoryFactory,
    CategoryGroupFactory,
    UserGroupFactory,
)


def test_create_group(session) -> None:
    user = UserFactory()
    user_data = {
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "picture": user.picture,
    }
    data = CreateGroup(title="test_title", description="test_description")
    group = create_group(session, user.id, data)
    assert group.title == "test_title"
    assert group.description == "test_description"
    assert group.status == Status.ACTIVE
    assert group.admin.login == user_data["login"]
    assert group.admin.first_name == user_data["first_name"]
    assert group.admin.last_name == user_data["last_name"]
    assert group.admin.picture == user_data["picture"]


def test_add_user_in_group(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    db_user_group = (
        session.query(UserGroup)
        .filter(and_(UserGroup.group_id == group.id, UserGroup.user_id == user.id))
        .one_or_none()
    )
    assert db_user_group is None
    add_user_in_group(session, user.id, group.id)
    db_user_group = (
        session.query(UserGroup)
        .filter(and_(UserGroup.group_id == group.id, UserGroup.user_id == user.id))
        .one_or_none()
    )
    assert db_user_group.user_id == user.id
    assert db_user_group.status == Status.ACTIVE
    assert db_user_group.group_id == group.id
    assert db_user_group.date_join.strftime(
        "%Y-%m-%d"
    ) == datetime.date.today().strftime("%Y-%m-%d")


def test_add_inactive_user_in_group(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(group_id=group.id, user_id=user.id, status=models.Status.INACTIVE)
    db_user_group = (
        session.query(UserGroup)
        .filter(and_(UserGroup.group_id == group.id, UserGroup.user_id == user.id))
        .one_or_none()
    )
    assert db_user_group.user_id == user.id
    assert db_user_group.status == Status.INACTIVE
    assert db_user_group.group_id == group.id
    assert db_user_group.date_join.strftime(
        "%Y-%m-%d"
    ) == datetime.date.today().strftime("%Y-%m-%d")

    add_user_in_group(session, user.id, group.id)
    db_user_group = (
        session.query(UserGroup)
        .filter(and_(UserGroup.group_id == group.id, UserGroup.user_id == user.id))
        .one_or_none()
    )
    assert db_user_group.user_id == user.id
    assert db_user_group.status == Status.ACTIVE
    assert db_user_group.group_id == group.id
    assert db_user_group.date_join.strftime(
        "%Y-%m-%d"
    ) == datetime.date.today().strftime("%Y-%m-%d")


def test_read_users_group(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    UserGroupFactory(user_id=second_user.id, group_id=group.id)
    users_group = read_users_group(session, first_user.id, group.id)
    users = [first_user, second_user]
    for data, user in zip(users_group.users_group, users):
        assert data.user.login == user.login
        assert data.status == Status.ACTIVE
        assert data.date_join.strftime("%Y-%m-%d") == datetime.date.today().strftime(
            "%Y-%m-%d"
        )


def test_read_users_group_as_not_user_group(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    with pytest.raises(HTTPException) as ex_info:
        read_users_group(session, 9999, group.id)
    assert "You are not in this group!" in str(ex_info.value.detail)


def test_read_user_groups(session) -> None:
    first_user = UserFactory()
    first_group = GroupFactory(admin_id=first_user.id)
    second_group = GroupFactory(admin_id=first_user.id)
    users_group = read_user_groups(session, first_user.id)
    assert users_group.user_groups == []
    UserGroupFactory(user_id=first_user.id, group_id=first_group.id)
    UserGroupFactory(user_id=first_user.id, group_id=second_group.id)
    users_group = read_user_groups(session, first_user.id)
    groups = [first_group, second_group]
    for data, group in zip(users_group.user_groups, groups):
        assert data.group.id == group.id
        assert data.group.title == group.title
        assert data.group.status == Status.ACTIVE


def test_read_categories_group(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=group.id)
    data = read_categories_group(session, user.id, group.id)
    categories = [category]
    for x, y in zip(data.categories_group, categories):
        assert x.category.id == y.id
        assert x.category.title == y.title


def test_read_categories_group_as_non_user_group(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    with pytest.raises(HTTPException) as ex_info:
        read_categories_group(session, 9999, group.id)
    assert "You are not a user of this group!" in str(ex_info.value.detail)


def test_leave_group_user(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    UserGroupFactory(user_id=second_user.id, group_id=group.id)
    users_group = read_users_group(session, first_user.id, group.id)
    for user in users_group.users_group:
        assert user.status == Status.ACTIVE
    data = leave_group(session, second_user.id, group.id)
    assert data.user.id == second_user.id
    assert data.status == Status.INACTIVE


def test_leave_group_not_found(session) -> None:
    user = UserFactory()
    with pytest.raises(HTTPException) as ex_info:
        leave_group(session, user.id, 9999)
    assert "Group is not found" in str(ex_info.value.detail)


def test_leave_group_admin(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    assert group.status == Status.ACTIVE
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    UserGroupFactory(user_id=second_user.id, group_id=group.id)
    users_group = read_users_group(session, first_user.id, group.id)
    for user in users_group.users_group:
        assert user.status == Status.ACTIVE
    leave_group(session, first_user.id, group.id)
    users_group = read_users_group(session, first_user.id, group.id)
    for user in users_group.users_group:
        assert user.status == Status.INACTIVE
    db_group = session.query(models.Group).filter_by(id=group.id).one()
    assert db_group.status == Status.INACTIVE


def test_disband_group(session):
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    UserGroupFactory(user_id=second_user.id, group_id=group.id)
    data = disband_group(session, group.id)
    for user in data.users_group:
        assert user.status == Status.INACTIVE
    db_group = session.query(models.Group).filter_by(id=group.id).one()
    assert db_group.status == Status.INACTIVE


def test_remove_user(session):
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    UserGroupFactory(user_id=second_user.id, group_id=group.id)
    db_users_group = read_users_group(session, first_user.id, group.id)
    for user in db_users_group.users_group:
        assert user.status == Status.ACTIVE
    data = remove_user(session, first_user.id, group.id, second_user.id)
    assert data.user.id == second_user.id
    assert data.status == Status.INACTIVE


def test_remove_admin(session):
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    UserGroupFactory(user_id=second_user.id, group_id=group.id)
    db_group = session.query(models.Group).filter_by(id=group.id).one()
    assert db_group.status == Status.ACTIVE
    data = remove_user(session, first_user.id, group.id, first_user.id)
    for user in data.users_group:
        assert user.status == Status.INACTIVE
    db_group = session.query(models.Group).filter_by(id=group.id).one()
    assert db_group.status == Status.INACTIVE


def test_remove_user_as_non_admin(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    with pytest.raises(HTTPException) as ex_info:
        remove_user(session, second_user.id, group.id, first_user.id)
    assert "You are not admin in this group!" in str(ex_info.value.detail)


def test_remove_inactive_user(session) -> None:
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    UserGroupFactory(user_id=first_user.id, group_id=group.id)
    UserGroupFactory(
        user_id=second_user.id, group_id=group.id, status=models.Status.INACTIVE
    )
    with pytest.raises(HTTPException) as ex_info:
        remove_user(session, first_user.id, group.id, second_user.id)
    assert "The user is not active or does not exist in this group!" in str(
        ex_info.value.detail
    )
