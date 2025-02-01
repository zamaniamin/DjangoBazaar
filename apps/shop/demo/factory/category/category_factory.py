from factory import LazyAttribute
from factory.django import DjangoModelFactory
from faker import Faker

from apps.shop.models.category import Category

fake = Faker()


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = LazyAttribute(lambda _: fake.word())
    description = LazyAttribute(lambda _: fake.sentence())
    slug = LazyAttribute(lambda obj: fake.slug())
    parent = None  # Set to None by default, you can override in tests
