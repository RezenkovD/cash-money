import datetime
import unittest
from unittest.mock import Mock

import models
from dependencies import oauth
from schemas import CreateExpense
from tests.conftest import client, async_return
from tests.factories import (
    UserFactory,
    GroupFactory,
    UserGroupFactory,
    CategoryFactory,
    CategoryGroupFactory,
    ExpenseFactory,
)


class ExpensesTestCase(unittest.TestCase):
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
        self.first_group = GroupFactory(admin_id=self.user.id)
        UserGroupFactory(user_id=self.user.id, group_id=self.first_group.id)
        self.category = CategoryFactory()
        CategoryGroupFactory(category_id=self.category.id, group_id=self.first_group.id)
        self.second_group = GroupFactory(admin_id=self.user.id)
        UserGroupFactory(user_id=self.user.id, group_id=self.second_group.id)
        CategoryGroupFactory(
            category_id=self.category.id, group_id=self.second_group.id
        )

    def test_create_expense(self) -> None:
        expense = CreateExpense(
            descriptions="descriptions", amount=999.9, category_id=self.category.id
        )
        data = client.post(
            f"/expenses/group/{self.first_group.id}/",
            json={
                "descriptions": expense.descriptions,
                "amount": expense.amount,
                "category_id": expense.category_id,
            },
        )
        expense_data = {
            "id": data.json()["id"],
            "descriptions": expense.descriptions,
            "amount": expense.amount,
            "time": data.json()["time"],
            "category_group": {
                "group": {"id": self.first_group.id, "title": self.first_group.title},
                "category": {"title": self.category.title, "id": self.category.id},
            },
            "user": {"id": self.user.id, "login": self.user.login},
        }
        assert data.status_code == 200
        assert data.json() == expense_data

    def test_create_expense_another_group(self) -> None:
        expense = CreateExpense(
            descriptions="descriptions", amount=999.9, category_id=self.category.id
        )
        data = client.post(
            f"/expenses/group/{9999}/",
            json={
                "descriptions": expense.descriptions,
                "amount": expense.amount,
                "category_id": expense.category_id,
            },
        )
        assert data.status_code == 404

    def test_create_expense_inactive_user(self) -> None:
        group = GroupFactory(admin_id=self.user.id)
        UserGroupFactory(
            user_id=self.user.id, group_id=group.id, status=models.Status.INACTIVE
        )
        expense = CreateExpense(
            descriptions="descriptions", amount=999.9, category_id=self.category.id
        )
        data = client.post(
            f"/expenses/group/{group.id}/",
            json={
                "descriptions": expense.descriptions,
                "amount": expense.amount,
                "category_id": expense.category_id,
            },
        )
        assert data.status_code == 405

    def test_create_expense_another_category(self) -> None:
        expense = CreateExpense(
            descriptions="descriptions", amount=999.9, category_id=9999
        )
        data = client.post(
            f"/expenses/group/{self.first_group.id}/",
            json={
                "descriptions": expense.descriptions,
                "amount": expense.amount,
                "category_id": expense.category_id,
            },
        )
        assert data.status_code == 404

    def test_read_expenses_by_another_group(self) -> None:
        data = client.get("/expenses/group/9999/all-time")
        assert data.status_code == 404

    def test_read_expenses_by_group_all_time(self) -> None:
        first_expense = ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
        )
        ExpenseFactory(
            user_id=self.user.id,
            group_id=self.second_group.id,
            category_id=self.category.id,
        )
        data = client.get(f"/expenses/group/{self.first_group.id}/all-time")
        assert data.status_code == 200
        expenses_data = [
            {
                "id": first_expense.id,
                "descriptions": first_expense.descriptions,
                "amount": first_expense.amount,
                "time": data.json()[0]["time"],
                "category_group": {
                    "group": {
                        "id": self.first_group.id,
                        "title": self.first_group.title,
                    },
                    "category": {"title": self.category.title, "id": self.category.id},
                },
            },
        ]
        assert data.json() == expenses_data

    def test_read_expenses_by_group_month_exc(self) -> None:
        data = client.get(f"/expenses/group/{self.first_group.id}/11-2022")
        assert data.status_code == 422

    def test_read_expenses_by_group_month(self) -> None:
        time = datetime.datetime(2022, 12, 1)
        data = client.get(f"/expenses/group/{self.first_group.id}/2022-12")
        assert not data.json()
        expense = ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
            time=time,
        )

        time = datetime.datetime(2022, 11, 12)
        ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
            time=time,
        )

        data = client.get(f"/expenses/group/{self.first_group.id}/2022-12")
        expenses_data = [
            {
                "id": expense.id,
                "descriptions": expense.descriptions,
                "amount": expense.amount,
                "time": data.json()[0]["time"],
                "category_group": {
                    "group": {
                        "id": self.first_group.id,
                        "title": self.first_group.title,
                    },
                    "category": {"title": self.category.title, "id": self.category.id},
                },
            },
        ]
        assert data.json() == expenses_data

    def test_read_expenses_by_group_time_range(self):
        time = datetime.datetime(2022, 12, 12)
        expense = ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
            time=time,
        )
        time = datetime.datetime(2022, 11, 12)
        ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
            time=time,
        )
        data = client.get(
            f"/expenses/group/{self.first_group.id}/2022-12-09/2022-12-31/"
        )
        expenses_data = [
            {
                "id": expense.id,
                "descriptions": expense.descriptions,
                "amount": expense.amount,
                "time": data.json()[0]["time"],
                "category_group": {
                    "group": {
                        "id": self.first_group.id,
                        "title": self.first_group.title,
                    },
                    "category": {"title": self.category.title, "id": self.category.id},
                },
            },
        ]
        assert data.json() == expenses_data

    def test_read_expenses_by_group_time_range_date_exc(self):
        data = client.get(
            f"/expenses/group/{self.first_group.id}/2022-12-31/2022-12-09/"
        )
        assert data.status_code == 404

    def test_read_expenses_all_time(self) -> None:
        first_expense = ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
        )
        second_expense = ExpenseFactory(
            user_id=self.user.id,
            group_id=self.second_group.id,
            category_id=self.category.id,
        )
        data = client.get(f"/expenses/all-time")
        assert data.status_code == 200
        expenses_data = [
            {
                "id": first_expense.id,
                "descriptions": first_expense.descriptions,
                "amount": first_expense.amount,
                "time": data.json()[0]["time"],
                "category_group": {
                    "group": {
                        "id": self.first_group.id,
                        "title": self.first_group.title,
                    },
                    "category": {"title": self.category.title, "id": self.category.id},
                },
            },
            {
                "id": second_expense.id,
                "descriptions": second_expense.descriptions,
                "amount": second_expense.amount,
                "time": data.json()[1]["time"],
                "category_group": {
                    "group": {
                        "id": self.second_group.id,
                        "title": self.second_group.title,
                    },
                    "category": {"title": self.category.title, "id": self.category.id},
                },
            },
        ]
        assert data.json() == expenses_data

    def test_read_expenses_month_exc(self) -> None:
        data = client.get(f"/expenses/11-2022")
        assert data.status_code == 422

    def test_read_expenses_month(self) -> None:
        time = datetime.datetime(2022, 12, 1)
        data = client.get(f"/expenses/2022-12")
        assert not data.json()

        first_expense = ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
            time=time,
        )
        second_expense = ExpenseFactory(
            user_id=self.user.id,
            group_id=self.second_group.id,
            category_id=self.category.id,
            time=time,
        )

        time = datetime.datetime(2022, 11, 12)
        ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
            time=time,
        )

        data = client.get(f"/expenses/2022-12")
        expenses_data = [
            {
                "id": first_expense.id,
                "descriptions": first_expense.descriptions,
                "amount": first_expense.amount,
                "time": data.json()[0]["time"],
                "category_group": {
                    "group": {
                        "id": self.first_group.id,
                        "title": self.first_group.title,
                    },
                    "category": {"title": self.category.title, "id": self.category.id},
                },
            },
            {
                "id": second_expense.id,
                "descriptions": second_expense.descriptions,
                "amount": second_expense.amount,
                "time": data.json()[1]["time"],
                "category_group": {
                    "group": {
                        "id": self.second_group.id,
                        "title": self.second_group.title,
                    },
                    "category": {"title": self.category.title, "id": self.category.id},
                },
            },
        ]
        assert data.json() == expenses_data

    def test_read_expenses_time_range(self):
        time = datetime.datetime(2022, 12, 1)
        data = client.get(f"/expenses/2022-12-1/2022-12-12")
        assert not data.json()

        first_expense = ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
            time=time,
        )
        second_expense = ExpenseFactory(
            user_id=self.user.id,
            group_id=self.second_group.id,
            category_id=self.category.id,
            time=time,
        )

        time = datetime.datetime(2022, 11, 13)
        ExpenseFactory(
            user_id=self.user.id,
            group_id=self.first_group.id,
            category_id=self.category.id,
            time=time,
        )

        data = client.get(f"/expenses/2022-12-1/2022-12-12")
        expenses_data = [
            {
                "id": first_expense.id,
                "descriptions": first_expense.descriptions,
                "amount": first_expense.amount,
                "time": data.json()[0]["time"],
                "category_group": {
                    "group": {
                        "id": self.first_group.id,
                        "title": self.first_group.title,
                    },
                    "category": {"title": self.category.title, "id": self.category.id},
                },
            },
            {
                "id": second_expense.id,
                "descriptions": second_expense.descriptions,
                "amount": second_expense.amount,
                "time": data.json()[1]["time"],
                "category_group": {
                    "group": {
                        "id": self.second_group.id,
                        "title": self.second_group.title,
                    },
                    "category": {"title": self.category.title, "id": self.category.id},
                },
            },
        ]
        assert data.json() == expenses_data

    def test_read_expenses_time_range_date_exc(self):
        data = client.get(f"/expenses/2022-12-31/2022-12-09/")
        assert data.status_code == 404
