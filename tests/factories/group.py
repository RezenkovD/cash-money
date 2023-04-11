import datetime

import factory

from models import Group, GroupStatusEnum, UserGroup

from .base_factory import BaseFactory


class GroupFactory(BaseFactory):
    id = factory.Sequence(lambda n: n + 1)
    title = factory.Faker("word")
    description = factory.Faker("word")
    admin_id = None
    status = GroupStatusEnum.ACTIVE

    class Meta:
        model = Group


class UserGroupFactory(BaseFactory):
    user_id = factory.Sequence(lambda n: n)
    group_id = factory.Sequence(lambda n: n)
    date_join = datetime.date.today()
    status = GroupStatusEnum.ACTIVE

    class Meta:
        model = UserGroup
