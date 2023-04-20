import factory

from models import Icon, Color, IconColor

from .base_factory import BaseFactory


class IconFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    url = factory.Faker("word")

    class Meta:
        model = Icon


class ColorFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    code = factory.Faker("word")

    class Meta:
        model = Color


class IconColorFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    icon_id = factory.Sequence(lambda n: n)
    color_id = factory.Sequence(lambda n: n)

    class Meta:
        model = IconColor
