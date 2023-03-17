import unittest
from unittest.mock import Mock

from dependencies import oauth
from schemas import CreateCategory
from tests.conftest import client, async_return
from tests.factories import UserFactory, GroupFactory, UserGroupFactory, CategoryFactory


class CategoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.user = UserFactory(id=99)
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

    def test_create_category(self) -> None:
        first_category = CategoryFactory()
        category = CreateCategory(title="title")
        data = client.post(
            f"/categories/{self.group.id}/", json={"title": category.title}
        )
        assert data.status_code == 200
        category_data = {"title": category.title, "id": data.json()["id"]}
        assert data.json() == category_data

        data = client.post(
            f"/categories/{self.group.id}/", json={"title": first_category.title}
        )
        assert data.status_code == 200
        category_data = {
            "title": first_category.title,
            "id": first_category.id,
        }
        assert data.json() == category_data
