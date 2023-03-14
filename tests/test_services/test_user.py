from services import get_user
from tests.factories import UserFactory


def test_get_user(session) -> None:
    db_data = get_user(session, "test_user")
    assert db_data is None
    user = UserFactory()
    user_data = {
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "picture": user.picture,
    }
    db_data = get_user(session, user.login)
    assert db_data.login == user_data["login"]
    assert db_data.first_name == user_data["first_name"]
    assert db_data.last_name == user_data["last_name"]
    assert db_data.picture == user_data["picture"]
