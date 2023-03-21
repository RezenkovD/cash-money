import datetime

import pytest
from starlette.exceptions import HTTPException

import models
from schemas import CreateExpense
from services import create_expense
from tests.factories import (
    UserFactory,
    GroupFactory,
    UserGroupFactory,
    CategoryFactory,
    CategoryGroupFactory,
)


def test_create_expense(session) -> None:
    user = UserFactory()
    first_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=first_group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=first_group.id)

    first_expense = CreateExpense(
        descriptions="descriptions", amount=999.9, category_id=category.id
    )

    with pytest.raises(HTTPException) as ex_info:
        create_expense(session, 9999, first_expense, user.id)
    assert "You are not a user of this group!" in str(ex_info.value.detail)

    second_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(
        user_id=user.id, group_id=second_group.id, status=models.Status.INACTIVE
    )
    with pytest.raises(HTTPException) as ex_info:
        create_expense(session, second_group.id, first_expense, user.id)
    assert "The user is not active in this group!" in str(ex_info.value.detail)

    second_expense = CreateExpense(
        descriptions="descriptions",
        amount=999.9,
        category_id=9999,
    )
    with pytest.raises(HTTPException) as ex_info:
        create_expense(session, first_group.id, second_expense, user.id)
    assert "The group has no such category!" in str(ex_info.value.detail)

    data = create_expense(session, first_group.id, first_expense, user.id)

    db_expenses = session.query(models.Expense).all()
    assert len(db_expenses) == 1

    assert data.descriptions == first_expense.descriptions
    assert data.amount == first_expense.amount
    assert data.time.strftime("%Y-%m-%d %H:%M") == datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    assert data.user.id == user.id
    assert data.category_group.category.id == category.id
    assert data.category_group.group.id == first_group.id
