import datetime
import unittest
from unittest.mock import Mock

from dependencies import oauth
from enums import GroupStatusEnum
from schemas import GroupCreate
from tests.conftest import async_return, client
from tests.factories import (
    CategoryFactory,
    CategoryGroupFactory,
    GroupFactory,
    UserFactory,
    UserGroupFactory,
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
        group = GroupCreate(
            title="string", description="string", icon_url="string", color_code="string"
        )
        data = client.post(
            "/groups/",
            json={
                "title": group.title,
                "description": group.description,
                "icon_url": group.icon_url,
                "color_code": group.color_code,
            },
        )
        assert data.status_code == 200
        group_data = {
            "id": data.json()["id"],
            "title": group.title,
            "description": group.description,
            "status": GroupStatusEnum.ACTIVE,
            "admin": {
                "id": self.user.id,
                "login": self.user_dict["userinfo"]["email"],
                "first_name": self.user_dict["userinfo"]["given_name"],
                "last_name": self.user_dict["userinfo"]["family_name"],
                "picture": self.user_dict["userinfo"]["picture"],
            },
        }
        assert data.json() == group_data

    def test_read_user_group(self) -> None:
        oauth.google.authorize_access_token = Mock(
            return_value=async_return(self.user_dict)
        )
        client.get("/auth/")
        data = client.get("/groups/")
        assert data.status_code == 200
        user_data = {
            "user_groups": [
                {
                    "group": {
                        "id": self.group.id,
                        "title": self.group.title,
                        "description": self.group.description,
                        "status": GroupStatusEnum.ACTIVE,
                    },
                    "status": GroupStatusEnum.ACTIVE,
                    "date_join": datetime.date.today().strftime("%Y-%m-%d"),
                }
            ]
        }
        data = data.json()
        assert data == user_data

    def test_update_group(self) -> None:
        group = GroupCreate(
            title="string", description="string", icon_url="string", color_code="string"
        )
        data = client.put(
            f"/groups/{self.group.id}",
            json={
                "title": group.title,
                "description": group.description,
                "icon_url": group.icon_url,
                "color_code": group.color_code,
            },
        )
        assert data.status_code == 200
        group_data = {
            "id": self.group.id,
            "title": group.title,
            "description": group.description,
            "status": GroupStatusEnum.ACTIVE,
            "admin": {
                "id": self.user.id,
                "login": self.user_dict["userinfo"]["email"],
                "first_name": self.user_dict["userinfo"]["given_name"],
                "last_name": self.user_dict["userinfo"]["family_name"],
                "picture": self.user_dict["userinfo"]["picture"],
            },
        }
        assert data.json() == group_data

    def test_update_group_as_non_admin(self) -> None:
        group = GroupCreate(
            title="string", description="string", icon_url="string", color_code="string"
        )
        data = client.put(
            f"/groups/9999",
            json={
                "title": group.title,
                "description": group.description,
                "icon_url": group.icon_url,
                "color_code": group.color_code,
            },
        )
        assert data.status_code == 404

    def test_read_users_group(self) -> None:
        data = client.get(f"/groups/{self.group.id}/users/")
        assert data.status_code == 200
        data = data.json()
        users_group_data = {
            "users_group": [
                {
                    "status": GroupStatusEnum.ACTIVE,
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
            "status": GroupStatusEnum.INACTIVE,
            "date_join": datetime.date.today().strftime("%Y-%m-%d"),
        }
        data = data.json()
        assert data == user_group_data

    def test_leave_group_not_found(self) -> None:
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
                    "status": GroupStatusEnum.INACTIVE,
                    "date_join": datetime.date.today().strftime("%Y-%m-%d"),
                }
            ]
        }
        assert data == user_group_data

    def test_remove_user(self) -> None:
        second_user = UserFactory()
        UserGroupFactory(user_id=second_user.id, group_id=self.group.id)
        data = client.post(f"/groups/{self.group.id}/users/{second_user.id}/remove")
        user_group_data = {
            "user": {
                "id": second_user.id,
                "login": second_user.login,
                "first_name": second_user.first_name,
                "last_name": second_user.last_name,
                "picture": second_user.picture,
            },
            "status": GroupStatusEnum.INACTIVE,
            "date_join": datetime.date.today().strftime("%Y-%m-%d"),
        }
        assert data.status_code == 200
        assert data.json() == user_group_data

    def test_remove_inactive_user(self) -> None:
        second_user = UserFactory()
        UserGroupFactory(
            user_id=second_user.id,
            group_id=self.group.id,
            status=GroupStatusEnum.INACTIVE,
        )
        data = client.post(f"/groups/{self.group.id}/users/{second_user.id}/remove/")
        assert data.status_code == 405

    def test_remove_admin(self) -> None:
        second_user = UserFactory()
        UserGroupFactory(user_id=second_user.id, group_id=self.group.id)
        data = client.post(f"/groups/{self.group.id}/users/{self.user.id}/remove/")
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
                    "status": GroupStatusEnum.INACTIVE,
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
                    "status": GroupStatusEnum.INACTIVE,
                    "date_join": datetime.date.today().strftime("%Y-%m-%d"),
                },
            ]
        }
        assert data.json() == users_group_data

    def test_remove_user_as_non_admin(self) -> None:
        second_user = UserFactory()
        second_group = GroupFactory(admin_id=second_user.id)
        data = client.post(f"/groups/{second_group.id}/users/{second_user.id}/remove/")
        assert data.status_code == 404

    def test_read_categories_group(self) -> None:
        data = client.get(f"/groups/{self.group.id}/categories/")
        assert data.status_code == 200
        assert data.json() == {"categories_group": []}
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

    def test_read_categories_group_as_non_user_group(self) -> None:
        data = client.get(f"/groups/9999/categories/")
        assert data.status_code == 405
