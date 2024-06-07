from faker import Faker

from apps.shop.models.option import Option, OptionItem


class OptionFactory:
    faker = Faker()

    @staticmethod
    def create_option():
        return Option.objects.create(option_name="color")

    @classmethod
    def populate_demo_options(cls):
        cls.add_one_item()
        cls.add_multiple_items()

    @classmethod
    def add_one_item(cls, get_item: bool = False, quantity: int = 1):
        option_name = cls.create_option()
        option_item = OptionItem.objects.create(
            option_name=option_name, quantity=quantity
        )
        if get_item:
            return option_name, option_item
        return option_name

    @classmethod
    def add_multiple_items(cls, get_items: bool = False):
        option_name = cls.create_option()

        option_items = OptionItem.objects.bulk_create(
            [OptionItem(option_name=option_name, quantity=1)]
        )

        if get_items:
            return option_name, option_items
        return option_name
