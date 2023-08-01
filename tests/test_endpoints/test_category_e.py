import unittest
from unittest.mock import Mock

from dependencies import oauth
from enums import GroupStatusEnum
from schemas import CategoryCreate, IconColor
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
        self.icon_url = "icon_url"
        self.color_code = "color_code"
        UserGroupFactory(user_id=self.user.id, group_id=self.group.id)

    def test_read_categories_group(self) -> None:
        data = client.get(f"/groups/{self.group.id}/categories/")
        assert data.status_code == 200
        assert data.json() == {"categories_group": []}
        category = CategoryFactory()
        CategoryGroupFactory(
            category_id=category.id,
            group_id=self.group.id,
            icon_url=self.icon_url,
            color_code=self.color_code,
        )
        data = client.get(f"/groups/{self.group.id}/categories/")
        assert data.status_code == 200
        categories_group_data = {
            "categories_group": [
                {
                    "category": {
                        "title": category.title,
                        "id": category.id,
                    },
                    "color_code": self.color_code,
                    "icon_url": self.icon_url,
                }
            ]
        }
        assert data.json() == categories_group_data

    def test_read_categories_group_as_non_user_group(self) -> None:
        data = client.get(f"/groups/9999/categories/")
        assert data.status_code == 405

    def test_create_category(self) -> None:
        category = CategoryCreate(title="title", icon_url="string", color_code="string")
        data = client.post(
            f"/groups/{self.group.id}/categories/",
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
            f"/groups/{self.group.id}/categories/{category.id}",
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
            "/groups/9999/categories/",
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
            f"/groups/{group.id}/categories/",
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
            f"/groups/{self.group.id}/categories/",
            json={
                "title": category.title,
                "icon_url": "icon_url",
                "color_code": "color_code",
            },
        )
        assert data.status_code == 405
