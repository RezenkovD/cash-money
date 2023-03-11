from unittest.mock import Mock

from dependencies import oauth
from models import User
from services import get_user
from tests.conftest import client, async_return
from tests.factories import UserFactory


def test_auth_registration(session):
    user_dict = {
        "userinfo": {
            "email": "user_login",
            "given_name": "user_first_name",
            "family_name": "user_last_name",
            "picture": None,
        }
    }
    list_users = session.query(User).all()
    assert len(list_users) == 0

    oauth.google.authorize_access_token = Mock(return_value=async_return(user_dict))
    client.get("/auth/")
    list_users = session.query(User).all()
    assert len(list_users) == 1

    db_user = get_user(session, login=user_dict["userinfo"]["email"])
    assert db_user.login == user_dict["userinfo"]["email"]
    assert db_user.first_name == user_dict["userinfo"]["given_name"]
    assert db_user.last_name == user_dict["userinfo"]["family_name"]
    assert db_user.picture == user_dict["userinfo"]["picture"]


def test_auth_login(session):
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
    data = client.get("/auth/")
    assert data.headers["set-cookie"] is not None


def test_logout(session):
    data = client.get("/logout/")
    assert "set-cookie" is not data.headers.keys()
