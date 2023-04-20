import datetime

import factory

from models import Group, UserGroup
from enums import GroupStatusEnum

from .base_factory import BaseFactory


class GroupFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    title = factory.Faker("word")
    description = factory.Faker("word")
    admin_id = None
    status = GroupStatusEnum.ACTIVE
    icon_color_id = factory.Faker("word")

    class Meta:
        model = Group


class UserGroupFactory(BaseFactory):
    user_id = factory.Sequence(lambda n: n)
    group_id = factory.Sequence(lambda n: n)
    date_join = datetime.date.today()
    status = GroupStatusEnum.ACTIVE

    class Meta:
        model = UserGroup
