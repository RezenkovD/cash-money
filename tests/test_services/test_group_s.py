import datetime
from operator import and_

import pytest
from starlette.exceptions import HTTPException
from sqlalchemy.orm import joinedload

from models import Group, UserGroup
from enums import GroupStatusEnum
from schemas import GroupCreate
from services import (
    add_user_in_group,
    create_group,
    disband_group,
    leave_group,
    read_categories_group,
    read_user_groups,
    read_users_group,
    remove_user,
    update_group,
)
from tests.factories import (
    CategoryFactory,
    CategoryGroupFactory,
    GroupFactory,
    UserGroupFactory,
)


def test_create_group(session, dependence_factory) -> None:
    factories = dependence_factory
    group_data = GroupCreate(
        title="test_title",
        description="test_description",
        icon_url="string",
        color_code="string",
    )
    group = create_group(session, factories["first_user"].id, group_data)
    assert session.query(Group).filter_by(id=group.id).one_or_none() is not None
    assert group.title == group_data.title
    assert group.description == group_data.description
    assert group.status == GroupStatusEnum.ACTIVE
    assert group.admin.login == factories["first_user"].login
    assert group.admin.first_name == factories["first_user"].first_name
    assert group.admin.last_name == factories["first_user"].last_name
    assert group.admin.picture == factories["first_user"].picture
    assert group.icon_url == group_data.icon_url
    assert group.color_code == group_data.color_code


def test_update_group(session, dependence_factory) -> None:
    factories = dependence_factory
    group_data = GroupCreate(
        title="test_title",
        description="test_description",
        icon_url="string",
        color_code="string",
    )
    group = update_group(
        session, factories["first_user"].id, group_data, factories["first_group"].id
    )
    assert session.query(Group).filter_by(id=group.id).one_or_none() is not None
    assert group.title == group_data.title
    assert group.description == group_data.description
    assert group.status == GroupStatusEnum.ACTIVE
    assert group.admin.login == factories["first_user"].login
    assert group.admin.first_name == factories["first_user"].first_name
    assert group.admin.last_name == factories["first_user"].last_name
    assert group.admin.picture == factories["first_user"].picture
    assert group.icon_url == group_data.icon_url
    assert group.color_code == group_data.color_code


def test_update_group_as_non_admin(session, dependence_factory) -> None:
    factories = dependence_factory
    group_data = GroupCreate(
        title="test_title",
        description="test_description",
        icon_url="string",
        color_code="string",
    )
    with pytest.raises(HTTPException) as ex_info:
        update_group(session, 99999, group_data, factories["first_group"].id)
    assert "You are not an admin of this group!" in str(ex_info.value.detail)


def test_add_user_in_group(session, dependence_factory) -> None:
    factories = dependence_factory
    add_user_in_group(session, factories["second_user"].id, factories["first_group"].id)
    session.commit()
    db_user_group = (
        session.query(UserGroup)
        .filter(
            and_(
                UserGroup.group_id == factories["first_group"].id,
                UserGroup.user_id == factories["second_user"].id,
            )
        )
        .one_or_none()
    )
    assert db_user_group.user_id == factories["second_user"].id
    assert db_user_group.status == GroupStatusEnum.ACTIVE
    assert db_user_group.group_id == factories["first_group"].id
    assert db_user_group.date_join.strftime(
        "%Y-%m-%d"
    ) == datetime.date.today().strftime("%Y-%m-%d")


def test_add_inactive_user_in_group(session, dependence_factory) -> None:
    factories = dependence_factory
    UserGroupFactory(
        group_id=factories["first_group"].id,
        user_id=factories["second_user"].id,
        status=GroupStatusEnum.INACTIVE,
    )
    add_user_in_group(session, factories["second_user"].id, factories["first_group"].id)
    db_user_group = (
        session.query(UserGroup)
        .filter(
            and_(
                UserGroup.group_id == factories["first_group"].id,
                UserGroup.user_id == factories["second_user"].id,
            )
        )
        .one_or_none()
    )
    assert db_user_group.user_id == factories["second_user"].id
    assert db_user_group.status == GroupStatusEnum.ACTIVE
    assert db_user_group.group_id == factories["first_group"].id
    assert db_user_group.date_join.strftime(
        "%Y-%m-%d"
    ) == datetime.date.today().strftime("%Y-%m-%d")


def test_read_users_group(
    session, dependence_factory, add_second_user_in_group
) -> None:
    factories = dependence_factory
    users_group = (
        session.query(Group)
        .options(joinedload(Group.users_group))
        .filter_by(id=factories["first_group"].id)
        .one()
    )
    users = [factories["first_user"], factories["second_user"]]
    for data, user in zip(users_group.users_group, users):
        assert data.user.login == user.login
        assert data.status == GroupStatusEnum.ACTIVE
        assert data.date_join.strftime("%Y-%m-%d") == datetime.date.today().strftime(
            "%Y-%m-%d"
        )


def test_read_users_group_as_not_user_group(session, dependence_factory) -> None:
    with pytest.raises(HTTPException) as ex_info:
        read_users_group(session, 9999, dependence_factory["first_group"].id)
    assert "You are not in this group!" in str(ex_info.value.detail)


def test_read_groups_user(session, dependence_factory) -> None:
    factories = dependence_factory
    second_group = GroupFactory(
        admin_id=factories["first_user"].id,
    )
    UserGroupFactory(user_id=factories["first_user"].id, group_id=second_group.id)
    users_group = read_user_groups(session, factories["first_user"].id)
    groups = [factories["first_group"], second_group]
    for data, group in zip(users_group.user_groups, groups):
        assert data.group.id == group.id
        assert data.group.title == group.title
        assert data.group.status == GroupStatusEnum.ACTIVE


def test_read_categories_group(session, dependence_factory) -> None:
    factories = dependence_factory
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=factories["first_group"].id)
    data = read_categories_group(
        session, factories["first_user"].id, factories["first_group"].id
    )
    categories = [category]
    for data, category in zip(data.categories_group, categories):
        assert data.category.id == category.id
        assert data.category.title == category.title


def test_read_categories_group_as_non_user_group(session, dependence_factory) -> None:
    with pytest.raises(HTTPException) as ex_info:
        read_categories_group(session, 9999, dependence_factory["first_group"].id)
    assert "You are not a user of this group!" in str(ex_info.value.detail)


def test_leave_group_user(
    session, dependence_factory, add_second_user_in_group
) -> None:
    factories = dependence_factory
    data = leave_group(
        session, factories["second_user"].id, factories["first_group"].id
    )
    assert data.user.id == factories["second_user"].id
    assert data.status == GroupStatusEnum.INACTIVE
    inactive_user = (
        session.query(UserGroup)
        .filter_by(
            user_id=factories["second_user"].id,
            status=GroupStatusEnum.INACTIVE,
        )
        .one_or_none()
    )
    assert inactive_user is not None


def test_leave_group_not_found(session, dependence_factory) -> None:
    with pytest.raises(HTTPException) as ex_info:
        leave_group(session, dependence_factory["first_user"].id, 9999)
    assert "Group is not found" in str(ex_info.value.detail)


def test_leave_group_admin(
    session, dependence_factory, add_second_user_in_group
) -> None:
    factories = dependence_factory
    leave_group(session, factories["first_user"].id, factories["first_group"].id)
    users_group = (
        session.query(Group)
        .options(joinedload(Group.users_group))
        .filter_by(id=factories["first_group"].id)
        .one()
    )
    for user in users_group.users_group:
        assert user.status == GroupStatusEnum.INACTIVE
    db_group = session.query(Group).filter_by(id=factories["first_group"].id).one()
    assert db_group.status == GroupStatusEnum.INACTIVE


def test_disband_group(session, dependence_factory, add_second_user_in_group) -> None:
    factories = dependence_factory
    data = disband_group(session, factories["first_group"].id)
    for user in data.users_group:
        assert user.status == GroupStatusEnum.INACTIVE
    db_group = session.query(Group).filter_by(id=factories["first_group"].id).one()
    assert db_group.status == GroupStatusEnum.INACTIVE


def test_remove_user(session, dependence_factory, add_second_user_in_group) -> None:
    factories = dependence_factory
    data = remove_user(
        session,
        factories["first_user"].id,
        factories["first_group"].id,
        factories["second_user"].id,
    )
    assert data.user.id == factories["second_user"].id
    assert data.status == GroupStatusEnum.INACTIVE


def test_remove_admin(session, dependence_factory, add_second_user_in_group) -> None:
    factories = dependence_factory
    data = remove_user(
        session,
        factories["first_user"].id,
        factories["first_group"].id,
        factories["first_user"].id,
    )
    for user in data.users_group:
        assert user.status == GroupStatusEnum.INACTIVE
    db_group = session.query(Group).filter_by(id=factories["first_group"].id).one()
    assert db_group.status == GroupStatusEnum.INACTIVE


def test_remove_user_as_non_admin(
    session, dependence_factory, add_second_user_in_group
) -> None:
    factories = dependence_factory
    with pytest.raises(HTTPException) as ex_info:
        remove_user(
            session,
            factories["second_user"].id,
            factories["first_group"].id,
            factories["first_user"].id,
        )
    assert "You are not admin of this group!" in str(ex_info.value.detail)


def test_remove_inactive_user(session, dependence_factory) -> None:
    factories = dependence_factory
    UserGroupFactory(
        user_id=factories["second_user"].id,
        group_id=factories["first_group"].id,
        status=GroupStatusEnum.INACTIVE,
    )
    with pytest.raises(HTTPException) as ex_info:
        remove_user(
            session,
            factories["first_user"].id,
            factories["first_group"].id,
            factories["second_user"].id,
        )
    assert "The user is not active or does not exist in this group!" in str(
        ex_info.value.detail
    )
