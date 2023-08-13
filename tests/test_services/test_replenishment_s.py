import datetime

import pytest
from starlette.exceptions import HTTPException

from models import Replenishment
from schemas import ReplenishmentCreate
from services import (
    create_replenishment,
    read_replenishments,
    delete_replenishment,
    update_replenishment,
)
from tests.factories import ReplenishmentFactory, UserFactory


def test_create_replenishment(session) -> None:
    user = UserFactory()
    replenishment = ReplenishmentCreate(descriptions="descriptions", amount=999.9)
    data = create_replenishment(session, user.id, replenishment)
    db_replenishment = session.query(Replenishment).all()
    assert len(db_replenishment) == 1
    assert data.descriptions == replenishment.descriptions
    assert float(data.amount) == replenishment.amount
    assert data.time.strftime("%Y-%m-%d %H:%M") == datetime.datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M"
    )
    assert data.user.id == user.id


def test_update_replenishment(session) -> None:
    user = UserFactory()
    replenishment = ReplenishmentFactory(user_id=user.id)
    date_update_replenishment = ReplenishmentCreate(
        descriptions="descriptions", amount=999.9
    )
    data = update_replenishment(
        session, user.id, date_update_replenishment, replenishment.id
    )
    assert data.descriptions == date_update_replenishment.descriptions
    assert float(data.amount) == date_update_replenishment.amount
    assert data.time.strftime("%Y-%m-%d %H:%M") == datetime.datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M"
    )
    assert data.user.id == user.id


def test_delete_replenishment(session) -> None:
    user = UserFactory()
    replenishment = ReplenishmentFactory(user_id=user.id)
    db_expenses = session.query(Replenishment).all()
    assert len(db_expenses) == 1
    delete_replenishment(session, user.id, replenishment.id)
    db_expenses = session.query(Replenishment).all()
    assert len(db_expenses) == 0


def test_update_replenishment_another_user(session) -> None:
    first_user = UserFactory()
    replenishment = ReplenishmentFactory(user_id=first_user.id)
    second_user = UserFactory()
    date_update_replenishment = ReplenishmentCreate(
        descriptions="descriptions", amount=999.9
    )
    with pytest.raises(HTTPException) as ex_info:
        update_replenishment(
            session, second_user.id, date_update_replenishment, replenishment.id
        )
    assert "It's not your replenishment!" in str(ex_info.value.detail)


def test_read_replenishments_by_group_time_range_date_exc(session) -> None:
    user = UserFactory()
    start_date = datetime.datetime(2022, 12, 10)
    end_date = datetime.datetime(2022, 11, 22)
    with pytest.raises(HTTPException) as ex_info:
        read_replenishments(
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
        )
    assert "The start date cannot be older than the end date!" in str(
        ex_info.value.detail
    )


def test_read_replenishments_all_time(session) -> None:
    user = UserFactory()
    first_replenishments = ReplenishmentFactory(user_id=user.id)
    second_replenishments = ReplenishmentFactory(user_id=user.id)
    data = read_replenishments(user_id=user.id)
    expenses = [
        first_replenishments,
        second_replenishments,
    ]
    data = session.execute(data).fetchall()
    for data, expense in zip(data, expenses):
        data_instance = data[0]
        assert data_instance.id == expense.id
        assert data_instance.time == expense.time
        assert data_instance.amount == expense.amount
        assert data_instance.descriptions == expense.descriptions


def test_read_replenishments_month(session) -> None:
    user = UserFactory()

    time = datetime.datetime(2022, 12, 12)

    first_replenishments = ReplenishmentFactory(user_id=user.id)
    second_replenishments = ReplenishmentFactory(user_id=user.id, time=time)
    third_replenishments = ReplenishmentFactory(user_id=user.id, time=time)

    replenishments = [first_replenishments]
    data = read_replenishments(
        user_id=user.id,
        filter_date=datetime.date.today(),
    )
    data = session.execute(data).fetchall()
    assert len(data) == len(replenishments)
    for data, replenishments in zip(data, replenishments):
        data_instance = data[0]
        assert data_instance.id == replenishments.id
        assert data_instance.time == replenishments.time
        assert data_instance.amount == replenishments.amount
        assert data_instance.descriptions == replenishments.descriptions
        assert data_instance.user.id == user.id

    replenishments = [second_replenishments, third_replenishments]
    data = read_replenishments(user_id=user.id, filter_date=time)
    data = session.execute(data).fetchall()
    assert len(data) == len(replenishments)
    for data, replenishments in zip(data, replenishments):
        data_instance = data[0]
        assert data_instance.id == replenishments.id
        assert data_instance.time == replenishments.time
        assert data_instance.amount == replenishments.amount
        assert data_instance.descriptions == replenishments.descriptions
        assert data_instance.user.id == user.id


def test_read_replenishments_time_range(session) -> None:
    user = UserFactory()

    second_date = datetime.datetime(2022, 12, 10)
    third_date = datetime.datetime(2022, 12, 22)

    ReplenishmentFactory(user_id=user.id)
    second_replenishments = ReplenishmentFactory(
        user_id=user.id,
        time=second_date,
    )
    third_replenishments = ReplenishmentFactory(
        user_id=user.id,
        time=third_date,
    )

    replenishments = [second_replenishments, third_replenishments]
    data = read_replenishments(
        user_id=user.id,
        start_date=second_date,
        end_date=third_date,
    )
    data = session.execute(data).fetchall()
    assert len(data) == len(replenishments)
    for data, replenishments in zip(data, replenishments):
        data_instance = data[0]
        assert data_instance.id == replenishments.id
        assert data_instance.time == replenishments.time
        assert data_instance.amount == replenishments.amount
        assert data_instance.descriptions == replenishments.descriptions
        assert data_instance.user.id == user.id
