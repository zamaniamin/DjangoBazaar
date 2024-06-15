from faker import Faker

from apps.shop.models.attribute import Attribute, AttributeItem


class AttributeFactory:
    faker = Faker()
    attribute_name_type = "sneakers"
    attribute_name_size = "size"
    attribute_name = "type"
    attribute_name_black = "black"

    @classmethod
    def create_attribute(cls, attribute_name=""):
        if attribute_name:
            return Attribute.objects.create(name=attribute_name)
        return Attribute.objects.create(name=cls.attribute_name_type)

    @classmethod
    def add_one_attribute_item(cls, attribute_id):
        return AttributeItem.objects.create(
            attribute_id=attribute_id, name=cls.attribute_name
        )

    @classmethod
    def add_attribute_item_list(cls, attribute_id):
        items = [
            AttributeItem(attribute_id=attribute_id, name=cls.attribute_name),
            AttributeItem(attribute_id=attribute_id, name=cls.attribute_name_black),
        ]
        return AttributeItem.objects.bulk_create(items)

    @classmethod
    def create_attribute_list(cls):
        Attribute.objects.create(name=cls.attribute_name_type)
        Attribute.objects.create(name=cls.attribute_name_size)
