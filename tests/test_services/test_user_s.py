from services import get_user, calculate_user_balance
from tests.factories import ReplenishmentFactory, UserFactory


def test_get_user(session) -> None:
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


def test_read_user_current_balance(session, dependence_factory, activity) -> None:
    factories = dependence_factory
    activity = activity
    first_replenishment = ReplenishmentFactory(user_id=factories["first_user"].id)
    second_replenishment = ReplenishmentFactory(user_id=factories["first_user"].id)
    data = calculate_user_balance(session, factories["first_user"].id)
    assert data.balance == float(
        first_replenishment.amount
        + second_replenishment.amount
        - activity["first_expense"].amount
    )


def test_read_user_negative_current_balance(
    session, dependence_factory, activity
) -> None:
    factories = dependence_factory
    activity = activity
    data = calculate_user_balance(session, factories["first_user"].id)
    assert data.balance == -float(activity["first_expense"].amount)
