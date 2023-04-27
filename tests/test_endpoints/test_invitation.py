import datetime
import unittest
from unittest.mock import Mock

from dependencies import oauth
from enums import GroupStatusEnum, ResponseStatusEnum, UserResponseEnum
from tests.conftest import async_return, client
from tests.factories import (
    GroupFactory,
    InvitationFactory,
    UserFactory,
    UserGroupFactory,
    IconFactory,
    ColorFactory,
    IconColorFactory,
)


class InvitationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.first_user = UserFactory()
        self.second_user = UserFactory()
        self.user_dict = {
            "userinfo": {
                "email": self.first_user.login,
                "given_name": self.first_user.first_name,
                "family_name": self.first_user.last_name,
                "picture": self.first_user.picture,
            }
        }
        oauth.google.authorize_access_token = Mock(
            return_value=async_return(self.user_dict)
        )
        client.get("/auth/")
        self.icon = IconFactory()
        self.color = ColorFactory()
        self.icon_color = IconColorFactory(icon_id=self.icon.id, color_id=self.color.id)
        self.first_group = GroupFactory(
            admin_id=self.first_user.id, icon_color_id=self.icon_color.id
        )
        UserGroupFactory(user_id=self.first_user.id, group_id=self.first_group.id)
        self.second_group = GroupFactory(
            admin_id=self.second_user.id, icon_color_id=self.icon_color.id
        )
        UserGroupFactory(user_id=self.second_user.id, group_id=self.second_group.id)

    def test_create_invitation(self) -> None:
        data = client.post(
            "/invitations/",
            json={"group_id": self.first_group.id, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 200
        data = data.json()
        invitation_data = {
            "id": data["id"],
            "status": ResponseStatusEnum.PENDING,
            "recipient": {
                "id": self.second_user.id,
                "login": self.second_user.login,
                "first_name": self.second_user.first_name,
                "last_name": self.second_user.last_name,
                "picture": self.second_user.picture,
            },
            "group": {
                "title": self.first_group.title,
                "description": self.first_group.description,
                "id": self.first_group.id,
                "status": GroupStatusEnum.ACTIVE,
                "admin": {
                    "id": self.first_user.id,
                    "login": self.first_user.login,
                    "first_name": self.first_user.first_name,
                    "last_name": self.first_user.last_name,
                    "picture": self.first_user.picture,
                },
                "icon_color": {
                    "id": self.icon_color.id,
                    "icon": {"id": self.icon.id, "url": self.icon.url},
                    "color": {"id": self.color.id, "code": self.color.code},
                },
            },
            "creation_time": datetime.date.today().strftime("%Y-%m-%d"),
        }
        assert data == invitation_data

    def test_create_invitation_as_non_admin(self) -> None:
        data = client.post(
            "/invitations/",
            json={"group_id": 9999, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 404

    def test_create_invitation_to_inactive_group(self) -> None:
        third_group = GroupFactory(
            admin_id=self.first_user.id,
            status=GroupStatusEnum.INACTIVE,
            icon_color_id=self.icon_color.id,
        )
        UserGroupFactory(user_id=self.first_user.id, group_id=third_group.id)
        data = client.post(
            "/invitations/",
            json={"group_id": third_group.id, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 405

    def test_create_invitation_to_nonexistent_user(self) -> None:
        data = client.post(
            "/invitations/",
            json={"group_id": self.first_group.id, "recipient_id": 9999},
        )
        assert data.status_code == 404

    def test_create_invitation_to_group_user(self) -> None:
        UserGroupFactory(user_id=self.second_user.id, group_id=self.first_group.id)
        data = client.post(
            "/invitations/",
            json={"group_id": self.first_group.id, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 405

    def test_create_invitation_twice(self) -> None:
        data = client.post(
            "/invitations/",
            json={"group_id": self.first_group.id, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 200
        data = client.post(
            "/invitations/",
            json={"group_id": self.first_group.id, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 405

    def test_read_invitations(self) -> None:
        invitation = InvitationFactory(
            sender_id=self.second_user.id,
            recipient_id=self.first_user.id,
            group_id=self.second_group.id,
        )
        data = client.get("invitations/list/")
        assert data.status_code == 200
        data_invitation = [
            {
                "id": invitation.id,
                "status": invitation.status,
                "group": {
                    "title": self.second_group.title,
                    "description": self.second_group.description,
                    "id": self.second_group.id,
                    "status": GroupStatusEnum.ACTIVE,
                    "admin": {
                        "id": self.second_user.id,
                        "login": self.second_user.login,
                        "first_name": self.second_user.first_name,
                        "last_name": self.second_user.last_name,
                        "picture": self.second_user.picture,
                    },
                    "icon_color": {
                        "id": self.icon_color.id,
                        "icon": {"id": self.icon.id, "url": self.icon.url},
                        "color": {"id": self.color.id, "code": self.color.code},
                    },
                },
                "creation_time": datetime.date.today().strftime("%Y-%m-%d"),
            }
        ]
        assert data_invitation == data.json()

    def test_response_invitation(self) -> None:
        invitation = InvitationFactory(
            sender_id=self.second_user.id,
            recipient_id=self.first_user.id,
            group_id=self.second_group.id,
        )
        response = UserResponseEnum.ACCEPTED
        data = client.post(f"invitations/response/{invitation.id}?response={response}")
        assert data.status_code == 200
        invitation_data = {
            "id": invitation.id,
            "status": response,
            "group": {
                "title": self.second_group.title,
                "description": self.second_group.description,
                "id": self.second_group.id,
                "status": GroupStatusEnum.ACTIVE,
                "admin": {
                    "id": self.second_user.id,
                    "login": self.second_user.login,
                    "first_name": self.second_user.first_name,
                    "last_name": self.second_user.last_name,
                    "picture": self.second_user.picture,
                },
                "icon_color": {
                    "id": self.icon_color.id,
                    "icon": {"id": self.icon.id, "url": self.icon.url},
                    "color": {"id": self.color.id, "code": self.color.code},
                },
            },
            "creation_time": datetime.date.today().strftime("%Y-%m-%d"),
            "recipient": {
                "id": self.first_user.id,
                "login": self.first_user.login,
                "first_name": self.first_user.first_name,
                "last_name": self.first_user.last_name,
                "picture": self.first_user.picture,
            },
        }
        assert data.json() == invitation_data

        users = [self.second_user, self.first_user]
        group_users = client.get(f"/groups/{self.second_group.id}/users/")
        assert group_users.status_code == 200
        group_users = group_users.json()["users_group"]
        assert len(group_users) == len(users)
        for group_user, user in zip(group_users, users):
            assert group_user["user"]["id"] == user.id
            assert group_user["status"] == GroupStatusEnum.ACTIVE

    def test_response_invitation_not_found(self) -> None:
        response = UserResponseEnum.ACCEPTED
        data = client.post(f"invitations/response/{9999}?response={response}")
        assert data.status_code == 404

    def test_response_invitation_in_inactive_group(self) -> None:
        group = GroupFactory(
            admin_id=self.first_user.id, icon_color_id=self.icon_color.id
        )
        UserGroupFactory(user_id=self.first_user.id, group_id=group.id)
        invitation = InvitationFactory(
            sender_id=self.first_user.id,
            recipient_id=self.second_user.id,
            group_id=group.id,
        )
        data = client.post(f"/groups/{group.id}/leave/")
        assert data.status_code == 200

        user_dict = {
            "userinfo": {
                "email": self.second_user.login,
                "given_name": self.second_user.first_name,
                "family_name": self.second_user.last_name,
                "picture": self.second_user.picture,
            }
        }
        oauth.google.authorize_access_token = Mock(return_value=async_return(user_dict))
        client.get("/auth/")
        response = UserResponseEnum.ACCEPTED
        data = client.post(f"invitations/response/{invitation.id}?response={response}")
        assert data.status_code == 404
