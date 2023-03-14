from services import get_user
from tests.factories import UserFactory


def test_get_user(session) -> None:
    data = get_user(session, "test_user")
    assert data is None
    user = UserFactory()
    user_data = {
        "login": user.login,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "picture": user.picture,
    }
    data = get_user(session, user.login)
    assert data.login == user_data["login"]
    assert data.first_name == user_data["first_name"]
    assert data.last_name == user_data["last_name"]
    assert data.picture == user_data["picture"]
