import unittest
from unittest.mock import Mock

from dependencies import oauth
from enums import GroupStatusEnum
from schemas import CreateCategory, IconColor
from tests.conftest import async_return, client
from tests.factories import (
    CategoryFactory,
    CategoryGroupFactory,
    GroupFactory,
    UserFactory,
    UserGroupFactory,
)


class CategoryTestCase(unittest.TestCase):
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

    def test_create_category(self) -> None:
        category = CreateCategory(title="title", icon_url="string", color_code="string")
        data = client.post(
            f"/categories/{self.group.id}/",
            json={
                "title": category.title,
                "icon_url": category.icon_url,
                "color_code": category.color_code,
            },
        )
        assert data.status_code == 200
        category_data = {"title": category.title.lower(), "id": data.json()["id"]}
        assert data.json() == category_data

    def test_update_category(self) -> None:
        category = CategoryFactory()
        CategoryGroupFactory(category_id=category.id, group_id=self.group.id)
        icon_color = IconColor(icon_url="string", color_code="string")
        data = client.put(
            f"/categories/{self.group.id}/{category.id}",
            json={
                "icon_url": icon_color.icon_url,
                "color_code": icon_color.color_code,
            },
        )
        assert data.status_code == 200
        category_data = {"title": category.title.lower(), "id": data.json()["id"]}
        assert data.json() == category_data

    def test_create_category_not_admin(self) -> None:
        category = CategoryFactory()
        data = client.post(
            "/categories/9999/",
            json={
                "title": category.title,
                "icon_url": "icon_url",
                "color_code": "color_code",
            },
        )
        assert data.status_code == 404

    def test_create_category_inactive_group(self) -> None:
        category = CategoryFactory()
        group = GroupFactory(
            admin_id=self.user.id,
            status=GroupStatusEnum.INACTIVE,
        )
        UserGroupFactory(
            user_id=self.user.id,
            group_id=group.id,
            status=GroupStatusEnum.INACTIVE,
        )
        data = client.post(
            f"/categories/{group.id}/",
            json={
                "title": category.title,
                "icon_url": "icon_url",
                "color_code": "color_code",
            },
        )
        assert data.status_code == 405

    def test_create_category_exist(self) -> None:
        category = CategoryFactory()
        CategoryGroupFactory(category_id=category.id, group_id=self.group.id)
        data = client.post(
            f"/categories/{self.group.id}/",
            json={
                "title": category.title,
                "icon_url": "icon_url",
                "color_code": "color_code",
            },
        )
        assert data.status_code == 405
