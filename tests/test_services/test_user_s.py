import datetime
from services import (
    get_user,
    read_user_balance,
    read_user_total_expenses,
    read_user_total_replenishments,
)
from tests.factories import ReplenishmentFactory, UserFactory, ExpenseFactory


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
    data = read_user_balance(session, factories["first_user"].id)
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
    data = read_user_balance(session, factories["first_user"].id)
    assert data.balance == -float(activity["first_expense"].amount)


def test_user_percentage_increase_expenses_for_month(
    session, dependence_factory, activity
) -> None:
    factories = dependence_factory
    activity = activity
    filter_date = datetime.datetime(2022, 12, 12)
    second_expense = ExpenseFactory(
        user_id=factories["first_user"].id,
        group_id=factories["first_group"].id,
        category_id=activity["category"].id,
        time=filter_date,
    )
    filter_date = datetime.datetime(2023, 1, 12)
    third_expense = ExpenseFactory(
        user_id=factories["first_user"].id,
        group_id=factories["first_group"].id,
        category_id=activity["category"].id,
        time=filter_date,
    )
    data = read_user_total_expenses(
        db=session,
        user_id=factories["first_user"].id,
        filter_date=filter_date,
    )
    assert data.percentage_increase == float(
        (third_expense.amount - second_expense.amount) / second_expense.amount
    )


def test_user_percentage_increase_expenses_for_range_time(
    session, dependence_factory, activity
) -> None:
    factories = dependence_factory
    activity = activity
    filter_date = datetime.datetime(2022, 12, 7)
    ExpenseFactory(
        user_id=factories["first_user"].id,
        group_id=factories["first_group"].id,
        category_id=activity["category"].id,
        time=filter_date,
    )
    filter_date = datetime.datetime(2022, 12, 12)
    second_expense = ExpenseFactory(
        user_id=factories["first_user"].id,
        group_id=factories["first_group"].id,
        category_id=activity["category"].id,
        time=filter_date,
    )
    start_date = datetime.datetime(2022, 12, 20)
    end_date = datetime.datetime(2023, 1, 1)
    third_expense = ExpenseFactory(
        user_id=factories["first_user"].id,
        group_id=factories["first_group"].id,
        category_id=activity["category"].id,
        time=end_date,
    )
    data = read_user_total_expenses(
        db=session,
        user_id=factories["first_user"].id,
        start_date=start_date,
        end_date=end_date,
    )
    assert data.percentage_increase == float(
        (third_expense.amount - second_expense.amount) / second_expense.amount
    )


def test_user_percentage_increase_replenishments_for_range_time(
    session, dependence_factory, activity
) -> None:
    factories = dependence_factory
    filter_date = datetime.datetime(2022, 12, 7)
    ReplenishmentFactory(
        user_id=factories["first_user"].id,
        time=filter_date,
    )
    filter_date = datetime.datetime(2022, 12, 12)
    first_replenishments = ReplenishmentFactory(
        user_id=factories["first_user"].id,
        time=filter_date,
    )
    start_date = datetime.datetime(2022, 12, 20)
    end_date = datetime.datetime(2023, 1, 1)
    second_replenishments = ReplenishmentFactory(
        user_id=factories["first_user"].id,
        time=end_date,
    )
    data = read_user_total_replenishments(
        db=session,
        user_id=factories["first_user"].id,
        start_date=start_date,
        end_date=end_date,
    )
    assert data.percentage_increase == float(
        (second_replenishments.amount - first_replenishments.amount)
        / first_replenishments.amount
    )
