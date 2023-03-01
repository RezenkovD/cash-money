import asyncio
from unittest.mock import Mock

from dependencies import oauth
from services.user import get_users
from tests.conftest import client
from tests.factories import UserFactory


def async_return(result):
    as_res = asyncio.Future()
    as_res.set_result(result)
    return as_res


def test_auth(session):
    list_users = get_users(session)
    assert len(list_users) == 0
    user = UserFactory()
    user_dict = {
        "userinfo": {
            "email": user.login,
            "given_name": user.first_name,
            "family_name": user.last_name,
            "picture": user.picture,
        }
    }
    oauth.google.authorize_access_token = Mock(return_value=async_return(user_dict))
    response = client.get("/auth/")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "id": user.id,
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "picture": user.picture,
    }
    list_users = get_users(session)
    assert len(list_users) == 1
