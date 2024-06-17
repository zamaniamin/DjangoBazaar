from faker import Faker

from apps.shop.models.option import Option, OptionItem


class OptionFactory:
    faker = Faker()
    option_name_color = "color"
    option_name_size = "size"
    item_name = "red"
    item_name_black = "black"

    @classmethod
    def create_option(cls, option_name=""):
        if option_name:
            return Option.objects.create(option_name=option_name)
        return Option.objects.create(option_name=cls.option_name_color)

    @classmethod
    def add_one_option_item(cls, option_id):
        return OptionItem.objects.create(option_id=option_id, item_name=cls.item_name)

    @classmethod
    def add_option_item_list(cls, option_id):
        items = [
            OptionItem(option_id=option_id, item_name=cls.item_name),
            OptionItem(option_id=option_id, item_name=cls.item_name_black),
        ]
        return OptionItem.objects.bulk_create(items)

    @classmethod
    def create_option_list(cls):
        Option.objects.create(option_name=cls.option_name_color)
        Option.objects.create(option_name=cls.option_name_size)
