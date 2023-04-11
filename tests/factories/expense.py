import datetime

import factory
from factory.fuzzy import FuzzyFloat

from models import Expense

from .base_factory import BaseFactory


class ExpenseFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    descriptions = factory.Faker("word")
    amount = FuzzyFloat(50.0, 1000.0)
    time = datetime.datetime.utcnow()
    user_id = factory.Faker("id")
    group_id = factory.Faker("id")
    category_id = factory.Faker("id")

    class Meta:
        model = Expense
