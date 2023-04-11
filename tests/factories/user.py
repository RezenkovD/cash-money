import factory
from models import User

from .base_factory import BaseFactory


class UserFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    login = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    picture = None

    class Meta:
        model = User
