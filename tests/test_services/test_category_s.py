import pytest
from starlette.exceptions import HTTPException

from models import Category, CategoryGroup
from enums import GroupStatusEnum
from schemas import CategoryCreate, IconColor
from services import create_category, update_category
from tests.factories import (
    CategoryFactory,
    GroupFactory,
    UserFactory,
    UserGroupFactory,
    CategoryGroupFactory,
)


def test_create_category(session, dependence_factory) -> None:
    factories = dependence_factory
    category = CategoryCreate(title="BoOK", color_code="string", icon_url="string")
    data = create_category(
        session, factories["first_user"].id, factories["first_group"].id, category
    )
    db_category = session.query(Category).filter_by(id=data.id).one_or_none()
    assert db_category is not None
    db_category_group = (
        session.query(CategoryGroup).filter_by(category_id=data.id).one_or_none()
    )
    assert db_category_group is not None


def test_update_category(session, dependence_factory) -> None:
    factories = dependence_factory
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=factories["first_group"].id)
    icon_color = IconColor(color_code="string", icon_url="string")
    data = update_category(
        session,
        factories["first_user"].id,
        factories["first_group"].id,
        icon_color,
        category.id,
    )
    db_category_group = (
        session.query(CategoryGroup)
        .filter_by(category_id=data.id, group_id=factories["first_group"].id)
        .one_or_none()
    )
    assert db_category_group.icon_url == icon_color.icon_url
    assert db_category_group.color_code == icon_color.color_code


def test_update_non_mine_category(session, dependence_factory) -> None:
    factories = dependence_factory
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=factories["first_group"].id)
    icon_color = IconColor(color_code="string", icon_url="string")
    with pytest.raises(HTTPException) as ex_info:
        update_category(
            session,
            factories["first_user"].id,
            factories["first_group"].id,
            icon_color,
            9999,
        )
    assert "You do not have this category!" in str(ex_info.value.detail)


def test_create_category_not_admin(session, dependence_factory) -> None:
    factories = dependence_factory
    category = CategoryCreate(title="Book", color_code="string", icon_url="string")
    with pytest.raises(HTTPException) as ex_info:
        create_category(session, 9999, factories["first_group"].id, category)
    assert "You are not admin in this group!" in str(ex_info.value.detail)


def test_create_category_inactive_group(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id, status=GroupStatusEnum.INACTIVE)
    UserGroupFactory(
        user_id=user.id,
        group_id=group.id,
        status=GroupStatusEnum.INACTIVE,
    )
    category = CategoryCreate(title="Book", color_code="string", icon_url="string")
    with pytest.raises(HTTPException) as ex_info:
        create_category(session, user.id, group.id, category)
    assert "Group is not active!" in str(ex_info.value.detail)


def test_create_category_exist(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    category = CategoryCreate(title="BoOK", color_code="string", icon_url="string")
    create_category(session, user.id, group.id, category)
    category = CategoryCreate(title="BOoK", color_code="string", icon_url="string")
    with pytest.raises(HTTPException) as ex_info:
        create_category(session, user.id, group.id, category)
    assert "The category is already in this group!" in str(ex_info.value.detail)


def test_add_exist_category_in_group(session, dependence_factory) -> None:
    factories = dependence_factory
    CategoryFactory(title="book")
    category = CategoryCreate(title="BOOK", color_code="string", icon_url="string")
    create_category(
        session,
        dependence_factory["first_user"].id,
        factories["first_group"].id,
        category,
    )
    db_category_group = session.query(CategoryGroup).all()
    assert len(db_category_group) == 1
