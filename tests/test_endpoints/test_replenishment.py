import datetime
import unittest
from unittest.mock import Mock

from dependencies import oauth
from schemas import CreateReplenishment
from tests.conftest import client, async_return
from tests.factories import UserFactory, ReplenishmentsFactory


class ReplenishmentsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.user_dict = {
            "userinfo": {
                "email": self.user.login,
                "given_name": self.user.first_name,
                "family_name": self.user.last_name,
                "picture": self.user.picture,
            }
        }
        oauth.google.authorize_access_token = Mock(
            return_value=async_return(self.user_dict)
        )
        client.get("/auth/")

    def test_create_replenishments(self) -> None:
        replenishments = CreateReplenishment(descriptions="descriptions", amount=999.9)
        data = client.post(
            "/replenishments/",
            json={
                "descriptions": replenishments.descriptions,
                "amount": replenishments.amount,
            },
        )
        replenishments_data = {
            "id": data.json()["id"],
            "descriptions": replenishments.descriptions,
            "amount": replenishments.amount,
            "time": data.json()["time"],
            "user": {"id": self.user.id, "login": self.user.login},
        }
        assert data.status_code == 200
        assert data.json() == replenishments_data

    def test_read_replenishments_all_time(self) -> None:
        first_replenishments = ReplenishmentsFactory(user_id=self.user.id)
        second_replenishments = ReplenishmentsFactory(user_id=self.user.id)
        data = client.get(f"/replenishments/all-time/")
        assert data.status_code == 200
        replenishments_data = [
            {
                "descriptions": first_replenishments.descriptions,
                "amount": float(first_replenishments.amount),
                "time": data.json()[0]["time"],
            },
            {
                "descriptions": second_replenishments.descriptions,
                "amount": float(second_replenishments.amount),
                "time": data.json()[1]["time"],
            },
        ]
        assert data.json() == replenishments_data

    def test_read_replenishments_month_exc(self) -> None:
        data = client.get(f"/replenishments/11-2022/")
        assert data.status_code == 422

    def test_read_replenishments_month(self) -> None:
        time = datetime.datetime(2022, 12, 1)
        data = client.get(f"/replenishments/2022-12/")
        assert not data.json()
        first_replenishments = ReplenishmentsFactory(user_id=self.user.id, time=time)
        second_replenishments = ReplenishmentsFactory(user_id=self.user.id, time=time)

        time = datetime.datetime(2022, 11, 12)
        ReplenishmentsFactory(user_id=self.user.id, time=time)

        data = client.get(f"/replenishments/2022-12/")
        replenishments_data = [
            {
                "descriptions": first_replenishments.descriptions,
                "amount": float(first_replenishments.amount),
                "time": data.json()[0]["time"],
            },
            {
                "descriptions": second_replenishments.descriptions,
                "amount": float(second_replenishments.amount),
                "time": data.json()[1]["time"],
            },
        ]
        assert data.json() == replenishments_data

    def test_read_replenishments_time_range(self) -> None:
        time = datetime.datetime(2022, 12, 1)
        data = client.get(f"/replenishments/2022-12-1/2022-12-12/")
        assert not data.json()
        first_replenishments = ReplenishmentsFactory(user_id=self.user.id, time=time)
        second_replenishments = ReplenishmentsFactory(user_id=self.user.id, time=time)
        time = datetime.datetime(2022, 11, 13)
        ReplenishmentsFactory(
            user_id=self.user.id,
            time=time,
        )
        data = client.get(f"/replenishments/2022-12-1/2022-12-12/")
        replenishments_data = [
            {
                "descriptions": first_replenishments.descriptions,
                "amount": float(first_replenishments.amount),
                "time": data.json()[0]["time"],
            },
            {
                "descriptions": second_replenishments.descriptions,
                "amount": float(second_replenishments.amount),
                "time": data.json()[1]["time"],
            },
        ]
        assert data.json() == replenishments_data

    def test_read_replenishments_time_range_date_exc(self) -> None:
        data = client.get(f"/replenishments/2022-12-31/2022-12-09/")
        assert data.status_code == 404
