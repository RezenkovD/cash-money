import datetime
import unittest
from unittest.mock import Mock

from dependencies import oauth
from tests.conftest import client, async_return
from tests.factories import UserFactory, GroupFactory, UserGroupFactory


class GroupTestCase(unittest.TestCase):
    def setUp(self):
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

    def test_create_group(self):
        data = client.post(
            "/groups/", json={"title": "string", "description": "string"}
        )
        group_data = {
            "title": "string",
            "description": "string",
            "admin": {
                "login": self.user_dict["userinfo"]["email"],
                "first_name": self.user_dict["userinfo"]["given_name"],
                "last_name": self.user_dict["userinfo"]["family_name"],
                "picture": self.user_dict["userinfo"]["picture"],
            },
        }
        assert data.status_code == 200
        assert data.json() == group_data

    def test_read_users_group(self):
        data = client.get(f"/groups/{self.group.id}/users")
        assert data.status_code == 200
        data = data.json()
        users_group_data = {
            "users_group": [
                {
                    "date_join": datetime.date.today().strftime("%Y-%m-%d"),
                    "user": {
                        "first_name": self.user.first_name,
                        "last_name": self.user.last_name,
                        "login": self.user.login,
                        "picture": self.user.picture,
                    },
                }
            ]
        }
        assert data == users_group_data
