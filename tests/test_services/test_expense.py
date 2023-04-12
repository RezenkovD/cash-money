import datetime

import pytest
from starlette.exceptions import HTTPException

from models import Expense
from enums import GroupStatusEnum
from schemas import CreateExpense
from services import create_expense, read_expenses
from tests.factories import (
    CategoryFactory,
    CategoryGroupFactory,
    ExpenseFactory,
    GroupFactory,
    UserFactory,
    UserGroupFactory,
)


def test_create_expense(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=group.id)
    expense = CreateExpense(
        descriptions="descriptions", amount=999.9, category_id=category.id
    )
    data = create_expense(session, user.id, group.id, expense)
    db_expenses = session.query(Expense).all()
    assert len(db_expenses) == 1
    assert data.descriptions == expense.descriptions
    assert float(data.amount) == expense.amount
    assert data.time.strftime("%Y-%m-%d %H:%M") == datetime.datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M"
    )
    assert data.user.id == user.id
    assert data.category_group.category.id == category.id
    assert data.category_group.group.id == group.id


def test_create_expense_another_group(session) -> None:
    user = UserFactory()
    category = CategoryFactory()
    expense = CreateExpense(
        descriptions="descriptions", amount=999.9, category_id=category.id
    )
    with pytest.raises(HTTPException) as ex_info:
        create_expense(session, user.id, 9999, expense)
    assert "You are not a user of this group!" in str(ex_info.value.detail)


def test_create_expense_inactive_user(session) -> None:
    user = UserFactory()
    category = CategoryFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(
        user_id=user.id,
        group_id=group.id,
        status=GroupStatusEnum.INACTIVE,
    )
    expense = CreateExpense(
        descriptions="descriptions", amount=999.9, category_id=category.id
    )
    with pytest.raises(HTTPException) as ex_info:
        create_expense(session, user.id, group.id, expense)
    assert "The user is not active in this group!" in str(ex_info.value.detail)


def test_create_expense_another_category(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    expense = CreateExpense(
        descriptions="descriptions",
        amount=999.9,
        category_id=9999,
    )
    with pytest.raises(HTTPException) as ex_info:
        create_expense(session, user.id, group.id, expense)
    assert "The group has no such category!" in str(ex_info.value.detail)


def test_read_expenses_by_another_group(session) -> None:
    with pytest.raises(HTTPException) as ex_info:
        read_expenses(session, 9999, 9999)
    assert "You are not a user of this group!" in str(ex_info.value.detail)


def test_read_expenses_by_group_all_time(session) -> None:
    user = UserFactory()
    first_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=first_group.id)
    second_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=second_group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=first_group.id)
    CategoryGroupFactory(category_id=category.id, group_id=second_group.id)

    first_expense = ExpenseFactory(
        user_id=user.id, group_id=first_group.id, category_id=category.id
    )
    second_expense = ExpenseFactory(
        user_id=user.id, group_id=second_group.id, category_id=category.id
    )
    third_expense = ExpenseFactory(
        user_id=user.id, group_id=first_group.id, category_id=category.id
    )

    data = read_expenses(db=session, group_id=first_group.id, user_id=user.id)
    expenses = [first_expense, third_expense]
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions
        assert data.category_group.group.id == expense.group_id
        assert data.category_group.category.id == expense.category_id

    data = read_expenses(db=session, group_id=second_group.id, user_id=user.id)
    expenses = [second_expense]
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions
        assert data.category_group.group.id == expense.group_id
        assert data.category_group.category.id == expense.category_id


def test_read_expenses_by_group_month(session) -> None:
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=group.id)

    time = datetime.datetime(2022, 12, 12)
    data = read_expenses(
        db=session,
        group_id=group.id,
        user_id=user.id,
        filter_date=datetime.date.today(),
    )
    assert not data

    data = read_expenses(
        db=session, group_id=group.id, user_id=user.id, filter_date=time
    )
    assert not data

    first_expense = ExpenseFactory(
        user_id=user.id, group_id=group.id, category_id=category.id
    )
    second_expense = ExpenseFactory(
        user_id=user.id, group_id=group.id, category_id=category.id, time=time
    )
    third_expense = ExpenseFactory(
        user_id=user.id, group_id=group.id, category_id=category.id, time=time
    )

    expenses = [first_expense]
    data = read_expenses(
        db=session,
        group_id=group.id,
        user_id=user.id,
        filter_date=datetime.date.today(),
    )
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions
        assert data.category_group.group.id == expense.group_id
        assert data.category_group.category.id == expense.category_id

    expenses = [second_expense, third_expense]
    data = read_expenses(
        db=session, group_id=group.id, user_id=user.id, filter_date=time
    )
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions
        assert data.category_group.group.id == expense.group_id
        assert data.category_group.category.id == expense.category_id


def test_read_expenses_by_group_time_range(session):
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=group.id)

    second_date = datetime.datetime(2022, 12, 10)
    third_date = datetime.datetime(2022, 12, 22)

    data = read_expenses(
        db=session,
        group_id=group.id,
        user_id=user.id,
        start_date=second_date,
        end_date=third_date,
    )
    assert not data

    ExpenseFactory(user_id=user.id, group_id=group.id, category_id=category.id)
    second_expense = ExpenseFactory(
        user_id=user.id, group_id=group.id, category_id=category.id, time=second_date
    )
    third_expense = ExpenseFactory(
        user_id=user.id, group_id=group.id, category_id=category.id, time=third_date
    )
    expenses = [second_expense, third_expense]

    data = read_expenses(
        db=session,
        group_id=group.id,
        user_id=user.id,
        start_date=second_date,
        end_date=third_date,
    )
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions
        assert data.category_group.group.id == expense.group_id
        assert data.category_group.category.id == expense.category_id


def test_read_expenses_by_group_time_range_date_exc(session):
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    start_date = datetime.datetime(2022, 12, 10)
    end_date = datetime.datetime(2022, 11, 22)
    with pytest.raises(HTTPException) as ex_info:
        read_expenses(
            db=session,
            group_id=group.id,
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
        )
    assert "The start date cannot be older than the end date!" in str(
        ex_info.value.detail
    )


def test_read_expenses_many_arguments(session):
    user = UserFactory()
    group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=group.id)
    filter_date = datetime.datetime(2022, 11, 10)
    start_date = datetime.datetime(2022, 11, 10)
    end_date = datetime.datetime(2022, 11, 10)
    with pytest.raises(HTTPException) as ex_info:
        read_expenses(
            db=session,
            group_id=group.id,
            user_id=user.id,
            filter_date=filter_date,
            start_date=start_date,
            end_date=end_date,
        )
    assert "Too many arguments!" in str(ex_info.value.detail)


def test_read_expenses_all_time(session):
    user = UserFactory()
    first_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=first_group.id)
    second_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=second_group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=first_group.id)
    CategoryGroupFactory(category_id=category.id, group_id=second_group.id)

    first_expense = ExpenseFactory(
        user_id=user.id, group_id=first_group.id, category_id=category.id
    )
    second_expense = ExpenseFactory(
        user_id=user.id, group_id=second_group.id, category_id=category.id
    )

    data = read_expenses(db=session, user_id=user.id)
    expenses = [
        first_expense,
        second_expense,
    ]
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions
        assert data.category_group.group.id == expense.group_id
        assert data.category_group.category.id == expense.category_id


def test_read_expenses_month(session):
    user = UserFactory()
    first_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=first_group.id)
    second_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=second_group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=first_group.id)
    CategoryGroupFactory(category_id=category.id, group_id=second_group.id)

    time = datetime.datetime(2022, 12, 12)

    first_expense = ExpenseFactory(
        user_id=user.id, group_id=first_group.id, category_id=category.id
    )
    second_expense = ExpenseFactory(
        user_id=user.id, group_id=second_group.id, category_id=category.id, time=time
    )
    third_expense = ExpenseFactory(
        user_id=user.id, group_id=first_group.id, category_id=category.id, time=time
    )

    expenses = [first_expense]
    data = read_expenses(
        db=session,
        user_id=user.id,
        filter_date=datetime.date.today(),
    )
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions
        assert data.category_group.group.id == expense.group_id
        assert data.category_group.category.id == expense.category_id

    expenses = [second_expense, third_expense]
    data = read_expenses(db=session, user_id=user.id, filter_date=time)
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions
        assert data.category_group.group.id == expense.group_id
        assert data.category_group.category.id == expense.category_id


def test_read_expenses_time_range(session):
    user = UserFactory()
    first_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=first_group.id)
    second_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=second_group.id)
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=first_group.id)
    CategoryGroupFactory(category_id=category.id, group_id=second_group.id)

    second_date = datetime.datetime(2022, 12, 10)
    third_date = datetime.datetime(2022, 12, 22)

    ExpenseFactory(user_id=user.id, group_id=first_group.id, category_id=category.id)
    second_expense = ExpenseFactory(
        user_id=user.id,
        group_id=second_group.id,
        category_id=category.id,
        time=second_date,
    )
    third_expense = ExpenseFactory(
        user_id=user.id,
        group_id=first_group.id,
        category_id=category.id,
        time=third_date,
    )

    expenses = [second_expense, third_expense]
    data = read_expenses(
        db=session,
        user_id=user.id,
        start_date=second_date,
        end_date=third_date,
    )

    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions
        assert data.category_group.group.id == expense.group_id
        assert data.category_group.category.id == expense.category_id
