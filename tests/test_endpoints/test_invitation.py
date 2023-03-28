import datetime
import unittest
from unittest.mock import Mock

import models
from dependencies import oauth
from tests.conftest import client, async_return
from tests.factories import (
    UserFactory,
    GroupFactory,
    UserGroupFactory,
    InvitationFactory,
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
        self.first_group = GroupFactory(admin_id=self.first_user.id)
        UserGroupFactory(user_id=self.first_user.id, group_id=self.first_group.id)
        self.second_group = GroupFactory(admin_id=self.second_user.id)
        UserGroupFactory(user_id=self.second_user.id, group_id=self.second_group.id)

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
                    "status": models.Status.ACTIVE,
                    "admin": {
                        "id": self.second_user.id,
                        "login": self.second_user.login,
                        "first_name": self.second_user.first_name,
                        "last_name": self.second_user.last_name,
                        "picture": self.second_user.picture,
                    },
                },
                "creation_time": datetime.date.today().strftime("%Y-%m-%d"),
            }
        ]
        assert data_invitation == data.json()

    def test_create_invitation(self) -> None:
        data = client.post(
            "/invitations/",
            json={"group_id": self.first_group.id, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 200
        data = data.json()
        invitation_data = {
            "id": data["id"],
            "status": models.ResponseStatus.PENDING,
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
                "status": models.Status.ACTIVE,
                "admin": {
                    "id": self.first_user.id,
                    "login": self.first_user.login,
                    "first_name": self.first_user.first_name,
                    "last_name": self.first_user.last_name,
                    "picture": self.first_user.picture,
                },
            },
            "creation_time": datetime.date.today().strftime("%Y-%m-%d"),
        }
        assert data == invitation_data

        data = client.post(
            "/invitations/",
            json={"group_id": self.first_group.id, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 405

        data = client.post(
            "/invitations/",
            json={"group_id": self.first_group.id, "recipient_id": 9999},
        )
        assert data.status_code == 404

        data = client.post(
            "/invitations/",
            json={"group_id": 9999, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 404

        third_group = GroupFactory(
            admin_id=self.first_user.id, status=models.Status.INACTIVE
        )
        UserGroupFactory(user_id=self.first_user.id, group_id=third_group.id)
        data = client.post(
            "/invitations/",
            json={"group_id": third_group.id, "recipient_id": self.second_user.id},
        )
        assert data.status_code == 405

    def test_response_invitation(self) -> None:
        invitation = InvitationFactory(
            sender_id=self.second_user.id,
            recipient_id=self.first_user.id,
            group_id=self.second_group.id,
        )
        response = models.UserResponse.ACCEPTED
        data = client.post(f"invitations/response/{invitation.id}?response={response}")
        assert data.status_code == 200
        invitation_data = {
            "id": invitation.id,
            "status": response,
            "group": {
                "title": self.second_group.title,
                "description": self.second_group.description,
                "id": self.second_group.id,
                "status": models.Status.ACTIVE,
                "admin": {
                    "id": self.second_user.id,
                    "login": self.second_user.login,
                    "first_name": self.second_user.first_name,
                    "last_name": self.second_user.last_name,
                    "picture": self.second_user.picture,
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
        group_users = client.get(f"/groups/{self.second_group.id}/users")
        assert group_users.status_code == 200
        group_users = group_users.json()["users_group"]
        for group_user, user in zip(group_users, users):
            assert group_user["user"]["id"] == user.id
            assert group_user["status"] == models.Status.ACTIVE
