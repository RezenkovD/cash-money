import datetime

import factory

from models import Invitation
from .base_factory import BaseFactory


class InvitationFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    sender_id = factory.Faker("id")
    recipient_id = factory.Faker("id")
    group_id = factory.Faker("id")
    creation_time = datetime.datetime.utcnow()
    status = "awaiting"

    class Meta:
        model = Invitation
