from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from apps.shop.models.attribute import Attribute, AttributeItem

fake = Faker()
ATTRIBUTE_COUNT = 2


class AttributeFactory(DjangoModelFactory):
    class Meta:
        model = Attribute

    attribute_name = LazyAttribute(lambda _: fake.word())

    @classmethod
    def create_with_items(cls, attribute_name=None, item_count=1):
        """
        Create an attribute and optionally attach multiple attribute items.
        """
        # Use Faker's `unique` feature to guarantee uniqueness
        attribute_name = attribute_name if attribute_name else fake.word()

        # Create the attribute instance
        attribute = cls(attribute_name=attribute_name)

        # Create associated attribute items
        for _ in range(item_count):
            AttributeItemFactory(attribute=attribute)

        return attribute

    @classmethod
    def generate_multiple(cls, count=ATTRIBUTE_COUNT, item_count=1, get_payload=False):
        """
        Generate multiple attributes, each optionally with associated attribute items.

        Args:
            count (int): The number of attributes to generate.
            item_count (int): The number of items to associate with each attribute.

        Returns:
            list: A list of generated Attribute instances.
        """
        attributes = []
        for _ in range(count):
            attributes.append(cls.create_with_items(item_count=item_count))
        if get_payload:
            payload = []
            for attribute in attributes:
                payload.append(
                    {
                        "attribute_id": attribute.id,
                        "items_id": list(attribute.items.values_list("id", flat=True)),
                    }
                )
            return payload, attributes
        return attributes


class AttributeItemFactory(DjangoModelFactory):
    class Meta:
        model = AttributeItem

    item_name = LazyAttribute(lambda _: fake.word())
    attribute = SubFactory(
        AttributeFactory
    )  # Automatically link to an Attribute instance
