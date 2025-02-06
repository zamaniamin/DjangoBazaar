from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from apps.shop.models.attribute import Attribute, AttributeItem

fake = Faker()


class AttributeFactory(DjangoModelFactory):
    class Meta:
        model = Attribute

    attribute_name = LazyAttribute(lambda _: fake.word())

    @classmethod
    def create_with_items(cls, attribute_name=None, item_count=1):
        """
        Create an attribute and optionally attach multiple attribute items.
        """
        attribute = cls(attribute_name=attribute_name) if attribute_name else cls()
        for _ in range(item_count):
            AttributeItemFactory(attribute=attribute)
        return attribute


class AttributeItemFactory(DjangoModelFactory):
    class Meta:
        model = AttributeItem

    item_name = LazyAttribute(lambda _: fake.word())
    attribute = SubFactory(
        AttributeFactory
    )  # Automatically link to an Attribute instance
