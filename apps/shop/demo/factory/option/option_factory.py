from faker import Faker

from apps.shop.models.option import Option, OptionItem


class OptionFactory:
    faker = Faker()
    option_name = "color"
    item_name = "red"

    @classmethod
    def create_option(cls):
        return Option.objects.create(option_name=cls.option_name)

    @classmethod
    def add_one_option_item(cls, option_id):
        return OptionItem.objects.create(option_id=option_id, item_name=cls.item_name)

    # @classmethod
    # def populate_demo_options(cls):
    #     cls.add_one_option_item()
    #     cls.add_multiple_items()
