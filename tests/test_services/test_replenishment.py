import datetime

import pytest
from starlette.exceptions import HTTPException

import models
from schemas import CreateReplenishment
from services import create_replenishments, read_replenishments
from tests.factories import ReplenishmentsFactory, UserFactory


def test_create_replenishments(session) -> None:
    user = UserFactory()
    replenishments = CreateReplenishment(descriptions="descriptions", amount=999.9)
    data = create_replenishments(session, user.id, replenishments)
    db_replenishments = session.query(models.Replenishment).all()
    assert len(db_replenishments) == 1
    assert data.descriptions == replenishments.descriptions
    assert float(data.amount) == replenishments.amount
    assert data.time.strftime("%Y-%m-%d %H:%M") == datetime.datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M"
    )
    assert data.user.id == user.id


def test_read_replenishments_by_group_time_range_date_exc(session) -> None:
    user = UserFactory()
    start_date = datetime.datetime(2022, 12, 10)
    end_date = datetime.datetime(2022, 11, 22)
    with pytest.raises(HTTPException) as ex_info:
        read_replenishments(
            db=session,
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
        )
    assert "The start date cannot be older than the end date!" in str(
        ex_info.value.detail
    )


def test_read_replenishments_many_arguments(session) -> None:
    user = UserFactory()
    filter_date = datetime.datetime(2022, 11, 10)
    start_date = datetime.datetime(2022, 11, 10)
    end_date = datetime.datetime(2022, 11, 10)
    with pytest.raises(HTTPException) as ex_info:
        read_replenishments(
            db=session,
            user_id=user.id,
            filter_date=filter_date,
            start_date=start_date,
            end_date=end_date,
        )
    assert (
        "Too many arguments! It is necessary to select either a month or a start date and an end date!"
        in str(ex_info.value.detail)
    )


def test_read_replenishments_all_time(session) -> None:
    user = UserFactory()
    first_replenishments = ReplenishmentsFactory(user_id=user.id)
    second_replenishments = ReplenishmentsFactory(user_id=user.id)
    data = read_replenishments(db=session, user_id=user.id)
    expenses = [
        first_replenishments,
        second_replenishments,
    ]
    assert len(data) == len(expenses)
    for data, expense in zip(data, expenses):
        assert data.id == expense.id
        assert data.time == expense.time
        assert data.amount == expense.amount
        assert data.descriptions == expense.descriptions


def test_read_replenishments_month(session) -> None:
    user = UserFactory()

    time = datetime.datetime(2022, 12, 12)

    first_replenishments = ReplenishmentsFactory(user_id=user.id)
    second_replenishments = ReplenishmentsFactory(user_id=user.id, time=time)
    third_replenishments = ReplenishmentsFactory(user_id=user.id, time=time)

    replenishments = [first_replenishments]
    data = read_replenishments(
        db=session,
        user_id=user.id,
        filter_date=datetime.date.today(),
    )
    assert len(data) == len(replenishments)
    for data, replenishments in zip(data, replenishments):
        assert data.id == replenishments.id
        assert data.time == replenishments.time
        assert data.amount == replenishments.amount
        assert data.descriptions == replenishments.descriptions
        assert data.user.id == user.id

    replenishments = [second_replenishments, third_replenishments]
    data = read_replenishments(db=session, user_id=user.id, filter_date=time)
    assert len(data) == len(replenishments)
    for data, replenishments in zip(data, replenishments):
        assert data.id == replenishments.id
        assert data.time == replenishments.time
        assert data.amount == replenishments.amount
        assert data.descriptions == replenishments.descriptions
        assert data.user.id == user.id


def test_read_replenishments_time_range(session) -> None:
    user = UserFactory()

    second_date = datetime.datetime(2022, 12, 10)
    third_date = datetime.datetime(2022, 12, 22)

    ReplenishmentsFactory(user_id=user.id)
    second_replenishments = ReplenishmentsFactory(
        user_id=user.id,
        time=second_date,
    )
    third_replenishments = ReplenishmentsFactory(
        user_id=user.id,
        time=third_date,
    )

    replenishments = [second_replenishments, third_replenishments]
    data = read_replenishments(
        db=session,
        user_id=user.id,
        start_date=second_date,
        end_date=third_date,
    )
    assert len(data) == len(replenishments)
    for data, replenishments in zip(data, replenishments):
        assert data.id == replenishments.id
        assert data.time == replenishments.time
        assert data.amount == replenishments.amount
        assert data.descriptions == replenishments.descriptions
        assert data.user.id == user.id
