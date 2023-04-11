from services import get_user

from tests.factories import UserFactory


def test_get_user(session) -> None:
    db_user = get_user(session, "test_user")
    assert db_user is None
    user = UserFactory()
    user_data = {
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "picture": user.picture,
    }
    db_user = get_user(session, user.login)
    assert db_user.login == user_data["login"]
    assert db_user.first_name == user_data["first_name"]
    assert db_user.last_name == user_data["last_name"]
    assert db_user.picture == user_data["picture"]
