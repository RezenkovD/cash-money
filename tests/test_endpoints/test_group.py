import datetime
import unittest
from unittest.mock import Mock

from dependencies import oauth
from models import Status
from schemas import CreateGroup
from tests.conftest import client, async_return
from tests.factories import UserFactory, GroupFactory, UserGroupFactory


class GroupTestCase(unittest.TestCase):
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
        self.group = GroupFactory(admin_id=self.user.id)
        self.user_group = UserGroupFactory(user_id=self.user.id, group_id=self.group.id)

    def test_create_group(self) -> None:
        group = CreateGroup(title="string", description="string")
        data = client.post(
            "/groups/", json={"title": group.title, "description": group.description}
        )
        group_data = data.json()
        group_data = {
            "id": group_data["id"],
            "title": group.title,
            "description": group.description,
            "status": Status.ACTIVE,
            "admin": {
                "id": self.user.id,
                "login": self.user_dict["userinfo"]["email"],
                "first_name": self.user_dict["userinfo"]["given_name"],
                "last_name": self.user_dict["userinfo"]["family_name"],
                "picture": self.user_dict["userinfo"]["picture"],
            },
        }
        assert data.status_code == 200
        assert data.json() == group_data

    def test_read_users_group(self) -> None:
        data = client.get(f"/groups/{self.group.id}/users")
        assert data.status_code == 200
        data = data.json()
        users_group_data = {
            "users_group": [
                {
                    "status": Status.ACTIVE,
                    "date_join": datetime.date.today().strftime("%Y-%m-%d"),
                    "user": {
                        "id": self.user.id,
                        "first_name": self.user.first_name,
                        "last_name": self.user.last_name,
                        "login": self.user.login,
                        "picture": self.user.picture,
                    },
                }
            ]
        }
        assert data == users_group_data
