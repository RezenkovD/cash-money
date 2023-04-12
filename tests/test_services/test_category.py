import pytest
from starlette.exceptions import HTTPException

from models import Category, CategoryGroups
from enums import GroupStatusEnum
from schemas import CreateCategory
from services import create_category
from tests.factories import CategoryFactory, GroupFactory, UserFactory, UserGroupFactory


def test_create_category(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    category = CreateCategory(title="BoOK")
    data = create_category(session, user.id, group.id, category)
    assert data.title == category.title.lower()
    db_category_group = session.query(CategoryGroups).all()
    assert len(db_category_group) == 1


def test_create_category_not_admin(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    category = CreateCategory(title="Book")
    with pytest.raises(HTTPException) as ex_info:
        create_category(session, 9999, group.id, category)
    assert "You are not admin in this group!" in str(ex_info.value.detail)


def test_create_category_inactive_group(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id, status=GroupStatusEnum.INACTIVE)
    UserGroupFactory(
        user_id=user.id,
        group_id=group.id,
        status=GroupStatusEnum.INACTIVE,
    )
    category = CreateCategory(title="Book")
    with pytest.raises(HTTPException) as ex_info:
        create_category(session, user.id, group.id, category)
    assert "Group is not active!" in str(ex_info.value.detail)


def test_create_category_exist(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    category = CreateCategory(title="BoOK")
    create_category(session, user.id, group.id, category)
    category = CreateCategory(title="BOoK")
    with pytest.raises(HTTPException) as ex_info:
        create_category(session, user.id, group.id, category)
    assert "The category is already in this group!" in str(ex_info.value.detail)


def test_add_exist_category_in_group(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    CategoryFactory(title="BOOK")
    db_category_group = session.query(Category).all()
    assert len(db_category_group) == 1
    category = CreateCategory(title="BOOK")
    data = create_category(session, user.id, group.id, category)
    assert data.title == category.title.lower()
    db_category_group = session.query(CategoryGroups).all()
    assert len(db_category_group) == 1
