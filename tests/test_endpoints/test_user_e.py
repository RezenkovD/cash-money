import unittest
from unittest.mock import Mock

from dependencies import oauth
from tests.conftest import async_return, client
from tests.factories import (
    CategoryFactory,
    CategoryGroupFactory,
    ExpenseFactory,
    GroupFactory,
    ReplenishmentFactory,
    UserFactory,
    UserGroupFactory,
)


class UserTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.first_user = UserFactory()
        self.second_user = UserFactory()
        self.users_data = [
            {
                "id": self.first_user.id,
                "login": self.first_user.login,
                "first_name": self.first_user.first_name,
                "last_name": self.first_user.last_name,
                "picture": self.first_user.picture,
            },
            {
                "id": self.second_user.id,
                "login": self.second_user.login,
                "first_name": self.second_user.first_name,
                "last_name": self.second_user.last_name,
                "picture": self.second_user.picture,
            },
        ]
        self.user_dict = {
            "userinfo": {
                "email": self.first_user.login,
                "given_name": self.first_user.first_name,
                "family_name": self.first_user.last_name,
                "picture": self.first_user.picture,
            }
        }

    def test_read_users(self) -> None:
        data = client.get("/users/")
        assert data.status_code == 200
        assert data.json() == self.users_data

    def test_read_user_current_balance(self) -> None:
        oauth.google.authorize_access_token = Mock(
            return_value=async_return(self.user_dict)
        )
        client.get("/auth/")
        group = GroupFactory(admin_id=self.first_user.id)
        UserGroupFactory(user_id=self.first_user.id, group_id=group.id)
        category = CategoryFactory()
        CategoryGroupFactory(category_id=category.id, group_id=group.id)

        first_replenishments = ReplenishmentFactory(user_id=self.first_user.id)
        second_replenishments = ReplenishmentFactory(user_id=self.first_user.id)
        first_expense = ExpenseFactory(
            user_id=self.first_user.id, group_id=group.id, category_id=category.id
        )
        second_expense = ExpenseFactory(
            user_id=self.first_user.id, group_id=group.id, category_id=category.id
        )
        balance = (
            first_replenishments.amount
            + second_replenishments.amount
            - (first_expense.amount + second_expense.amount)
        )
        data = client.get("/users/user-balance/")
        assert data.status_code == 200
        assert data.json() == {"balance": float(balance)}
