from faker import Faker

from apps.shop.models.attribute import Attribute, AttributeItem


class AttributeFactory:
    faker = Faker()
    attribute_name = "sample attribute"
    attribute_name_2 = "sample attribute 2"
    attribute_item_name = "sample item"
    attribute_item_name_2 = "sample item 2"

    @classmethod
    def create_attribute(cls, attribute_name=""):
        if attribute_name:
            return Attribute.objects.create(attribute_name=attribute_name)
        return Attribute.objects.create(attribute_name=cls.attribute_name)

    @classmethod
    def add_one_attribute_item(cls, attribute_id):
        return AttributeItem.objects.create(
            attribute_id=attribute_id, item_name=cls.attribute_item_name
        )

    @classmethod
    def add_attribute_item_list(cls, attribute_id):
        items = [
            AttributeItem(attribute_id=attribute_id, item_name=cls.attribute_item_name),
            AttributeItem(
                attribute_id=attribute_id, item_name=cls.attribute_item_name_2
            ),
        ]
        return AttributeItem.objects.bulk_create(items)

    @classmethod
    def create_attribute_list(cls):
        Attribute.objects.create(attribute_name=cls.attribute_name)
        Attribute.objects.create(attribute_name=cls.attribute_name_2)
