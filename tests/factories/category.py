import factory

from models import Category, CategoryGroups

from .base_factory import BaseFactory


class CategoryFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    title = factory.Faker("word")

    class Meta:
        model = Category


class CategoryGroupFactory(BaseFactory):
    category_id = factory.Sequence(lambda n: n)
    group_id = factory.Sequence(lambda n: n)

    class Meta:
        model = CategoryGroups
