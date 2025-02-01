from factory import LazyAttribute, post_generation
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

    @post_generation
    def children(self, create, extracted, **kwargs):
        """
        Optional children relationship.
        You can pass a number like CategoryFactory(children=3) to create 3 children.
        """
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of children were passed in, so create them
            for child in range(extracted):
                CategoryFactory(parent=self)
