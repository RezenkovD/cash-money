import pytest
from starlette.exceptions import HTTPException

import models
from schemas import CreateCategory
from services import create_category
from tests.factories import UserFactory, GroupFactory, UserGroupFactory, CategoryFactory


def test_create_category(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    category = CreateCategory(title="Book")
    data = create_category(session, group.id, category, user.id)
    assert data.title == category.title.lower()

    with pytest.raises(HTTPException) as ex_info:
        create_category(session, group.id, category, user.id)
    assert "The category is already in this group!" in str(ex_info.value.detail)

    db_category_group = session.query(models.CategoryGroups).all()
    assert len(db_category_group) == 1

    second_category = CategoryFactory()
    data = create_category(session, group.id, second_category, user.id)
    assert data.title == second_category.title.lower()

    db_category_group = session.query(models.CategoryGroups).all()
    assert len(db_category_group) == 2

    with pytest.raises(HTTPException) as ex_info:
        create_category(session, group.id, category, 9999)
    assert "You are not admin in this group!" in str(ex_info.value.detail)
