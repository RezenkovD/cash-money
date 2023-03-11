import datetime
from operator import and_

from models import UserGroup
from schemas import CreateGroup
from services import create_group, add_user_in_group, read_users_group, read_user_groups
from tests.factories import UserFactory, GroupFactory


def test_create_group(session):
    user = UserFactory()
    user_data = {
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "picture": user.picture,
    }
    group = CreateGroup(title="test_title", description="test_description")
    data = create_group(session, group, user.id)
    assert data.title == "test_title"
    assert data.description == "test_description"
    assert data.admin.login == user_data["login"]
    assert data.admin.first_name == user_data["first_name"]
    assert data.admin.last_name == user_data["last_name"]
    assert data.admin.picture == user_data["picture"]


def test_add_user_in_group(session):
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    data = (
        session.query(UserGroup)
        .filter(and_(UserGroup.group_id == group.id, UserGroup.user_id == user.id))
        .one_or_none()
    )
    assert data is None
    add_user_in_group(session, group.id, user.id)
    data = (
        session.query(UserGroup)
        .filter(and_(UserGroup.group_id == group.id, UserGroup.user_id == user.id))
        .one_or_none()
    )
    assert data.user_id == user.id
    assert data.group_id == group.id
    assert data.date_join.strftime("%Y %m %d") == datetime.date.today().strftime(
        "%Y %m %d"
    )


def test_read_users_group(session):
    first_user = UserFactory()
    second_user = UserFactory()
    group = GroupFactory(admin_id=first_user.id)
    add_user_in_group(session, group.id, first_user.id)
    add_user_in_group(session, group.id, second_user.id)
    data = read_users_group(session, group.id, first_user.id)
    list_user = [first_user, second_user]
    for x, y in zip(data.users_group, list_user):
        assert x.user.login == y.login
        assert x.date_join.strftime("%Y %m %d") == datetime.date.today().strftime(
            "%Y %m %d"
        )


def test_read_user_groups(session):
    first_user = UserFactory()
    first_group = GroupFactory(admin_id=first_user.id)
    second_group = GroupFactory(admin_id=first_user.id)
    data = read_user_groups(session, first_user.id)
    assert data.user_groups == []
    add_user_in_group(session, first_group.id, first_user.id)
    add_user_in_group(session, second_group.id, first_user.id)
    data = read_user_groups(session, first_user.id)
    list_group = [first_group, second_group]
    for x, y in zip(data.user_groups, list_group):
        assert x.group.title == y.title
