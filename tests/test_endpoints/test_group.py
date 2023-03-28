import datetime
import unittest
from unittest.mock import Mock

from dependencies import oauth
from models import Status
from schemas import CreateGroup
from tests.conftest import client, async_return
from tests.factories import (
    UserFactory,
    GroupFactory,
    UserGroupFactory,
    CategoryFactory,
    CategoryGroupFactory,
)


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
        UserGroupFactory(user_id=self.user.id, group_id=self.group.id)

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
        data = client.get(f"/groups/{self.group.id}/users/")
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

    def test_leave_group_user(self) -> None:
        second_user = UserFactory()
        second_group = GroupFactory(admin_id=second_user.id)
        UserGroupFactory(user_id=second_user.id, group_id=second_group.id)
        UserGroupFactory(user_id=self.user.id, group_id=second_group.id)
        data = client.post(f"/groups/{second_group.id}/leave/")
        assert data.status_code == 200
        user_group_data = {
            "user": {
                "id": self.user.id,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "login": self.user.login,
                "picture": self.user.picture,
            },
            "status": Status.INACTIVE,
            "date_join": datetime.date.today().strftime("%Y-%m-%d"),
        }
        data = data.json()
        assert data == user_group_data

        data = client.post(f"/groups/9999/leave/")
        assert data.status_code == 404

    def test_leave_group_admin(self) -> None:
        data = client.post(f"/groups/{self.group.id}/leave/")
        assert data.status_code == 200
        data = data.json()
        user_group_data = {
            "users_group": [
                {
                    "user": {
                        "id": self.user.id,
                        "first_name": self.user.first_name,
                        "last_name": self.user.last_name,
                        "login": self.user.login,
                        "picture": self.user.picture,
                    },
                    "status": Status.INACTIVE,
                    "date_join": datetime.date.today().strftime("%Y-%m-%d"),
                }
            ]
        }
        assert data == user_group_data

        data = client.post(f"/groups/9999/leave/")
        assert data.status_code == 404

    def test_remove_user(self) -> None:
        second_user = UserFactory()
        UserGroupFactory(user_id=second_user.id, group_id=self.group.id)
        data = client.post(f"/groups/{self.group.id}/remove/{second_user.id}/")
        user_group_data = {
            "user": {
                "id": second_user.id,
                "login": second_user.login,
                "first_name": second_user.first_name,
                "last_name": second_user.last_name,
                "picture": second_user.picture,
            },
            "status": Status.INACTIVE,
            "date_join": datetime.date.today().strftime("%Y-%m-%d"),
        }
        assert data.status_code == 200
        assert data.json() == user_group_data

        data = client.post(f"/groups/{self.group.id}/remove/{second_user.id}/")
        assert data.status_code == 405

        data = client.post(f"/groups/{self.group.id}/remove/{self.user.id}/")
        assert data.status_code == 200
        users_group_data = {
            "users_group": [
                {
                    "user": {
                        "id": self.user.id,
                        "first_name": self.user.first_name,
                        "last_name": self.user.last_name,
                        "login": self.user.login,
                        "picture": self.user.picture,
                    },
                    "status": Status.INACTIVE,
                    "date_join": datetime.date.today().strftime("%Y-%m-%d"),
                },
                {
                    "user": {
                        "id": second_user.id,
                        "login": second_user.login,
                        "first_name": second_user.first_name,
                        "last_name": second_user.last_name,
                        "picture": second_user.picture,
                    },
                    "status": Status.INACTIVE,
                    "date_join": datetime.date.today().strftime("%Y-%m-%d"),
                },
            ]
        }
        assert data.json() == users_group_data

    def test_read_categories_group(self) -> None:
        data = client.get(f"/groups/{self.group.id}/categories/")
        assert data.status_code == 200
        assert data.json() == {"categories_group": []}

        data = client.get(f"/groups/9999/categories/")
        assert data.status_code == 405

        category = CategoryFactory()
        CategoryGroupFactory(category_id=category.id, group_id=self.group.id)
        data = client.get(f"/groups/{self.group.id}/categories/")
        assert data.status_code == 200
        categories_group_data = {
            "categories_group": [
                {
                    "category": {
                        "title": category.title,
                        "id": category.id,
                    }
                }
            ]
        }
        assert data.json() == categories_group_data
