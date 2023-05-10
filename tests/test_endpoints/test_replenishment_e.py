import datetime
import unittest
from unittest.mock import Mock

from dependencies import oauth
from schemas import CreateReplenishment
from tests.conftest import async_return, client
from tests.factories import ReplenishmentFactory, UserFactory


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

    def test_create_replenishment(self) -> None:
        replenishment = CreateReplenishment(descriptions="descriptions", amount=999.9)
        data = client.post(
            "/replenishments/",
            json={
                "descriptions": replenishment.descriptions,
                "amount": replenishment.amount,
            },
        )
        replenishment_data = {
            "id": data.json()["id"],
            "descriptions": replenishment.descriptions,
            "amount": replenishment.amount,
            "time": data.json()["time"],
            "user": {"id": self.user.id, "login": self.user.login},
        }
        assert data.status_code == 200
        assert data.json() == replenishment_data

    def test_update_replenishment(self) -> None:
        replenishment = ReplenishmentFactory(user_id=self.user.id)
        date_update_replenishment = CreateReplenishment(
            descriptions="descriptions", amount=999.9
        )
        data = client.put(
            f"/replenishments/{replenishment.id}/",
            json={
                "descriptions": date_update_replenishment.descriptions,
                "amount": date_update_replenishment.amount,
            },
        )
        replenishments_data = {
            "id": data.json()["id"],
            "descriptions": date_update_replenishment.descriptions,
            "amount": date_update_replenishment.amount,
            "time": data.json()["time"],
            "user": {"id": self.user.id, "login": self.user.login},
        }
        assert data.status_code == 200
        assert data.json() == replenishments_data

    def test_delete_replenishment(self) -> None:
        replenishment = ReplenishmentFactory(user_id=self.user.id)
        data = client.delete(f"/replenishments/{replenishment.id}/")
        assert data.status_code == 204
        data = client.get(f"/replenishments/")
        assert data.status_code == 200
        replenishments_data = []
        assert data.json() == replenishments_data

    def test_read_replenishments_all_time(self) -> None:
        first_replenishments = ReplenishmentFactory(user_id=self.user.id)
        second_replenishments = ReplenishmentFactory(user_id=self.user.id)
        data = client.get(f"/replenishments/")
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

    def test_read_replenishments_exc_three_args(self) -> None:
        params = {
            "start_date": "2022-12-1",
            "end_date": "2022-12-12",
            "year_month": "2022-12",
        }
        data = client.get(f"/replenishments/", params=params)
        assert data.status_code == 422

    def test_read_replenishments_exc_args_no_match(self) -> None:
        params = {"end_date": "2022-12-12", "year_month": "2022-12"}
        data = client.get(f"/replenishments/", params=params)
        assert data.status_code == 422

    def test_read_replenishments_month_exc(self) -> None:
        params = {"year_month": "12-2022"}
        data = client.get(f"/replenishments/", params=params)
        assert data.status_code == 422

    def test_read_replenishments_month(self) -> None:
        time = datetime.datetime(2022, 12, 1)
        params = {"year_month": "2022-12"}
        data = client.get("/replenishments", params=params)
        assert not data.json()
        first_replenishments = ReplenishmentFactory(user_id=self.user.id, time=time)
        second_replenishments = ReplenishmentFactory(user_id=self.user.id, time=time)

        time = datetime.datetime(2022, 11, 12)
        ReplenishmentFactory(user_id=self.user.id, time=time)

        data = client.get("/replenishments/", params=params)
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
        params = {"start_date": "2022-12-1", "end_date": "2022-12-12"}
        data = client.get("/replenishments/", params=params)
        assert not data.json()
        first_replenishments = ReplenishmentFactory(user_id=self.user.id, time=time)
        second_replenishments = ReplenishmentFactory(user_id=self.user.id, time=time)
        time = datetime.datetime(2022, 11, 13)
        ReplenishmentFactory(
            user_id=self.user.id,
            time=time,
        )
        data = client.get("/replenishments/", params=params)
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
        params = {"start_date": "2022-12-31", "end_date": "2022-12-09"}
        data = client.get(f"/replenishments/", params=params)
        assert data.status_code == 404
