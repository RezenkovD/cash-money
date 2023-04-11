from services import get_user, read_user_current_balance
from tests.factories import (
    UserFactory,
    ReplenishmentsFactory,
    ExpenseFactory,
    GroupFactory,
    UserGroupFactory,
    CategoryFactory,
    CategoryGroupFactory,
)


def test_get_user(session) -> None:
    db_user = get_user(session, "test_user")
    assert db_user is None
    user = UserFactory()
    user_data = {
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "picture": user.picture,
    }
    db_user = get_user(session, user.login)
    assert db_user.login == user_data["login"]
    assert db_user.first_name == user_data["first_name"]
    assert db_user.last_name == user_data["last_name"]
    assert db_user.picture == user_data["picture"]


def test_read_user_positive_current_balance(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=group.id)

    first_replenishments = ReplenishmentsFactory(user_id=user.id)
    second_replenishments = ReplenishmentsFactory(user_id=user.id)
    first_expense = ExpenseFactory(
        user_id=user.id, group_id=group.id, category_id=category.id
    )
    second_expense = ExpenseFactory(
        user_id=user.id, group_id=group.id, category_id=category.id
    )
    data = read_user_current_balance(session, user.id)
    assert data.current_balance == float(
        first_replenishments.amount
        + second_replenishments.amount
        - (first_expense.amount + second_expense.amount)
    )


def test_read_user_negative_current_balance(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=group.id)

    first_expense = ExpenseFactory(
        user_id=user.id, group_id=group.id, category_id=category.id
    )
    second_expense = ExpenseFactory(
        user_id=user.id, group_id=group.id, category_id=category.id
    )
    data = read_user_current_balance(session, user.id)
    assert data.current_balance == float(
        -(first_expense.amount + second_expense.amount)
    )
