import datetime
from unittest.mock import Mock

from dependencies import oauth
from tests.conftest import client, async_return
from tests.factories import UserFactory, GroupFactory, UserGroupFactory


def test_read_users(session):
    first_user = UserFactory()
    second_user = UserFactory()
    users_data = [
        {
            "login": first_user.login,
            "first_name": first_user.first_name,
            "last_name": first_user.last_name,
            "picture": first_user.picture,
        },
        {
            "login": second_user.login,
            "first_name": second_user.first_name,
            "last_name": second_user.last_name,
            "picture": second_user.picture,
        },
    ]
    data = client.get("/users/")
    assert data.status_code == 200
    assert data.json() == users_data


def test_read_user_group(session):
    user = UserFactory()
    user_dict = {
        "userinfo": {
            "email": user.login,
            "given_name": user.first_name,
            "family_name": user.last_name,
            "picture": user.picture,
        }
    }
    oauth.google.authorize_access_token = Mock(
        return_value=async_return(user_dict)
    )
    client.get("/auth/")
    first_group = GroupFactory(admin_id=user.id)
    second_group = GroupFactory(admin_id=user.id)
    UserGroupFactory(user_id=user.id, group_id=first_group.id)
    UserGroupFactory(user_id=user.id, group_id=second_group.id)
    data = client.get("/users/groups/")
    assert data.status_code == 200
    data = data.json()
    user_data = {
        "user_groups": [
            {
                "group": {
                    "title": first_group.title,
                    "description": first_group.description
                },
                "date_join": datetime.date.today().strftime("%Y-%m-%d")
            },
            {
                "group": {
                    "title": second_group.title,
                    "description": second_group.description
                },
                "date_join": datetime.date.today().strftime("%Y-%m-%d")
            },
        ]
    }
    assert data == user_data
