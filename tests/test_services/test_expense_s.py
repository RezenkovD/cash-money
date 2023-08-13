import datetime

import pytest
from starlette.exceptions import HTTPException

from models import Expense
from enums import GroupStatusEnum
from schemas import ExpenseCreate
from services import create_expense
from services.expense import update_expense, delete_expense, read_expenses
from tests.factories import UserGroupFactory


def test_create_expense(session, dependence_factory, activity) -> None:
    factories = dependence_factory
    activity = activity
    expense = ExpenseCreate(
        descriptions="descriptions", amount=999.9, category_id=activity["category"].id
    )
    data = create_expense(
        session, factories["first_user"].id, factories["first_group"].id, expense
    )
    db_expenses = session.query(Expense).filter_by(id=data.id).one_or_none()
    assert db_expenses is not None
    assert data.descriptions == expense.descriptions
    assert float(data.amount) == expense.amount
    assert data.time.strftime("%Y-%m-%d %H:%M") == datetime.datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M"
    )
    assert data.user.id == factories["first_user"].id
    assert data.category_group.category.id == activity["category"].id
    assert data.category_group.group.id == factories["first_group"].id


def test_update_expense(session, dependence_factory, activity) -> None:
    factories = dependence_factory
    activity = activity
    date_update_expense = ExpenseCreate(
        descriptions="descriptions", amount=999.9, category_id=activity["category"].id
    )
    data = update_expense(
        session,
        factories["first_user"].id,
        factories["first_group"].id,
        date_update_expense,
        activity["first_expense"].id,
    )
    assert data.descriptions == date_update_expense.descriptions
    assert float(data.amount) == date_update_expense.amount
    assert data.time == activity["first_expense"].time
    assert data.user.id == factories["first_user"].id
    assert data.category_group.category.id == activity["category"].id
    assert data.category_group.group.id == factories["first_group"].id


def test_delete_expense(session, dependence_factory, activity) -> None:
    factories = dependence_factory
    activity = activity
    db_expenses = session.query(Expense).all()
    assert len(db_expenses) == 1
    delete_expense(
        session,
        factories["first_user"].id,
        factories["first_group"].id,
        activity["first_expense"].id,
    )
    db_expenses = session.query(Expense).all()
    assert len(db_expenses) == 0


def test_update_expense_another_user(session, dependence_factory, activity) -> None:
    factories = dependence_factory
    activity = activity
    UserGroupFactory(
        user_id=factories["second_user"].id, group_id=factories["first_group"].id
    )
    date_update_expense = ExpenseCreate(
        descriptions="descriptions", amount=999.9, category_id=activity["category"].id
    )
    with pytest.raises(HTTPException) as ex_info:
        update_expense(
            session,
            factories["second_user"].id,
            factories["first_group"].id,
            date_update_expense,
            activity["first_expense"].id,
        )
    assert "It's not your expense!" in str(ex_info.value.detail)


def test_create_expense_another_group(session, dependence_factory, activity) -> None:
    factories = dependence_factory
    activity = activity
    expense = ExpenseCreate(
        descriptions="descriptions", amount=999.9, category_id=activity["category"].id
    )
    with pytest.raises(HTTPException) as ex_info:
        create_expense(session, factories["first_user"].id, 9999, expense)
    assert "You are not a user of this group!" in str(ex_info.value.detail)


def test_create_expense_inactive_user(session, dependence_factory, activity) -> None:
    factories = dependence_factory
    activity = activity
    UserGroupFactory(
        user_id=factories["second_user"].id,
        group_id=factories["first_group"].id,
        status=GroupStatusEnum.INACTIVE,
    )
    expense = ExpenseCreate(
        descriptions="descriptions", amount=999.9, category_id=activity["category"].id
    )
    with pytest.raises(HTTPException) as ex_info:
        create_expense(
            session, factories["second_user"].id, factories["first_group"].id, expense
        )
    assert "The user is not active in this group!" in str(ex_info.value.detail)


def test_create_expense_another_category(session, dependence_factory) -> None:
    factories = dependence_factory
    expense = ExpenseCreate(
        descriptions="descriptions",
        amount=999.9,
        category_id=9999,
    )
    with pytest.raises(HTTPException) as ex_info:
        create_expense(
            session, factories["first_user"].id, factories["first_group"].id, expense
        )
    assert "The group has no such category!" in str(ex_info.value.detail)


def test_read_expenses_by_another_group(session) -> None:
    with pytest.raises(HTTPException) as ex_info:
        read_expenses(session, 9999, 9999)
    assert "You are not a user of this group!" in str(ex_info.value.detail)


def test_read_expenses_by_group_all_time(
    session, dependence_factory, activity, update_activity
) -> None:
    factories = dependence_factory
    activity = activity
    update_activity = update_activity
    expenses = [activity["first_expense"], update_activity["third_expense"]]
    data = read_expenses(
        db=session,
        group_id=factories["first_group"].id,
        user_id=factories["first_user"].id,
    )
    data = session.execute(data).fetchall()
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        data_instance = data[0]
        assert data_instance.id == expense.id
        assert data_instance.time == expense.time
        assert data_instance.amount == expense.amount
        assert data_instance.descriptions == expense.descriptions
        assert data_instance.category_group.group.id == expense.group_id
        assert data_instance.category_group.category.id == expense.category_id


def test_read_expenses_by_group_month(
    session, dependence_factory, activity, update_activity
) -> None:
    factories = dependence_factory
    activity = activity
    expenses = [activity["first_expense"]]
    data = read_expenses(
        db=session,
        group_id=factories["first_group"].id,
        user_id=factories["first_user"].id,
        filter_date=activity["filter_date"],
    )
    data = session.execute(data).fetchall()
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        data_instance = data[0]
        assert data_instance.id == expense.id
        assert data_instance.time == expense.time
        assert data_instance.amount == expense.amount
        assert data_instance.descriptions == expense.descriptions
        assert data_instance.category_group.group.id == expense.group_id
        assert data_instance.category_group.category.id == expense.category_id


def test_read_expenses_by_group_time_range(
    session, dependence_factory, activity, update_activity
):
    factories = dependence_factory
    update_activity = update_activity
    expenses = [update_activity["third_expense"]]
    data = read_expenses(
        db=session,
        group_id=factories["first_group"].id,
        user_id=factories["first_user"].id,
        start_date=update_activity["start_date"],
        end_date=update_activity["end_date"],
    )
    data = session.execute(data).fetchall()
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        data_instance = data[0]
        assert data_instance.id == expense.id
        assert data_instance.time == expense.time
        assert data_instance.amount == expense.amount
        assert data_instance.descriptions == expense.descriptions
        assert data_instance.category_group.group.id == expense.group_id
        assert data_instance.category_group.category.id == expense.category_id


def test_read_expenses_by_group_time_range_date_exc(session, dependence_factory):
    factories = dependence_factory
    start_date = datetime.datetime(2022, 12, 10)
    end_date = datetime.datetime(2022, 11, 22)
    with pytest.raises(HTTPException) as ex_info:
        read_expenses(
            db=session,
            group_id=factories["first_group"].id,
            user_id=factories["first_user"].id,
            start_date=start_date,
            end_date=end_date,
        )
    assert "The start date cannot be older than the end date!" in str(
        ex_info.value.detail
    )


def test_read_expenses_many_arguments(session, dependence_factory):
    factories = dependence_factory
    filter_date = datetime.datetime(2022, 11, 10)
    start_date = datetime.datetime(2022, 11, 10)
    end_date = datetime.datetime(2022, 11, 10)
    with pytest.raises(HTTPException) as ex_info:
        read_expenses(
            db=session,
            group_id=factories["first_group"].id,
            user_id=factories["first_user"].id,
            filter_date=filter_date,
            start_date=start_date,
            end_date=end_date,
        )
    assert "Too many arguments!" in str(ex_info.value.detail)


def test_read_expenses_all_time(session, dependence_factory, activity, update_activity):
    factories = dependence_factory
    activity = activity
    update_activity = update_activity
    data = read_expenses(db=session, user_id=factories["first_user"].id)
    data = session.execute(data).fetchall()
    expenses = [
        activity["first_expense"],
        update_activity["second_expense"],
        update_activity["third_expense"],
    ]
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        data_instance = data[0]
        assert data_instance.id == expense.id
        assert data_instance.time == expense.time
        assert data_instance.amount == expense.amount
        assert data_instance.descriptions == expense.descriptions
        assert data_instance.category_group.group.id == expense.group_id
        assert data_instance.category_group.category.id == expense.category_id


def test_read_expenses_month(session, dependence_factory, activity, update_activity):
    factories = dependence_factory
    update_activity = update_activity
    expenses = [update_activity["second_expense"], update_activity["third_expense"]]
    data = read_expenses(
        db=session,
        user_id=factories["first_user"].id,
        filter_date=update_activity["start_date"],
    )
    data = session.execute(data).fetchall()
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        data_instance = data[0]
        assert data_instance.id == expense.id
        assert data_instance.time == expense.time
        assert data_instance.amount == expense.amount
        assert data_instance.descriptions == expense.descriptions
        assert data_instance.category_group.group.id == expense.group_id
        assert data_instance.category_group.category.id == expense.category_id


def test_read_expenses_time_range(
    session, dependence_factory, activity, update_activity
):
    factories = dependence_factory
    update_activity = update_activity
    expenses = [update_activity["second_expense"], update_activity["third_expense"]]
    data = read_expenses(
        db=session,
        user_id=factories["first_user"].id,
        start_date=update_activity["start_date"],
        end_date=update_activity["end_date"],
    )
    data = session.execute(data).fetchall()
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        data_instance = data[0]
        assert data_instance.id == expense.id
        assert data_instance.time == expense.time
        assert data_instance.amount == expense.amount
        assert data_instance.descriptions == expense.descriptions
        assert data_instance.category_group.group.id == expense.group_id
        assert data_instance.category_group.category.id == expense.category_id
