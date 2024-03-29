import datetime

import factory

from models import Invitation
from enums import ResponseStatusEnum

from .base_factory import BaseFactory


class InvitationFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    sender_id = factory.Faker("id")
    recipient_id = factory.Faker("id")
    group_id = factory.Faker("id")
    creation_time = datetime.datetime.utcnow()
    status = ResponseStatusEnum.PENDING

    class Meta:
        model = Invitation
