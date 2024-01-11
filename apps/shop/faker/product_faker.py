import random

from faker import Faker
from faker.providers import lorem

from apps.shop.services.product_service import ProductService


class FakeProduct:
    """
    Populates the database with fake products.
    """

    fake = Faker()

    options = ["color", "size", "material", "Style"]
    option_color_items = ["red", "green", "black", "blue", "yellow"]
    option_size_items = ["S", "M", "L", "XL", "XXL"]
    option_material_items = ["Cotton", "Nylon", "Plastic", "Wool", "Leather"]
    option_style_items = ["Casual", "Formal"]

    def fill_products(self):
        """
        For generating fake products as demo.
        """
        self.fake.add_provider(lorem)

    @classmethod
    def generate_name(cls):
        return cls.fake.text(max_nb_chars=25)

    @classmethod
    def generate_description(cls):
        return cls.fake.paragraph(nb_sentences=5)

    @staticmethod
    def get_random_price():
        return round(random.uniform(1, 100), 2)

    @staticmethod
    def get_random_stock():
        return random.randint(0, 100)

    @classmethod
    def generate_uniq_options(cls):
        return [
            {"option_name": "color", "items": cls.option_color_items[:2]},
            {"option_name": "size", "items": cls.option_size_items[:2]},
            {"option_name": "material", "items": cls.option_material_items[:2]},
        ]

    @classmethod
    def get_payload(cls):
        payload = {
            "product_name": cls.generate_name(),
            "description": cls.generate_description(),
            "status": "active",
            "price": cls.get_random_price(),
            "stock": cls.get_random_stock(),
            "options": [],
        }
        return payload.copy()

    @classmethod
    def get_payload_with_options(cls):
        payload = {
            "product_name": cls.generate_name(),
            "description": cls.generate_description(),
            "status": "active",
            "price": cls.get_random_price(),
            "stock": cls.get_random_stock(),
            "options": cls.generate_uniq_options(),
        }
        return payload.copy()

    @classmethod
    def populate_product_with_options(cls):
        """
        Crete a product with options. (with all fields)
        """

        product_data = cls.get_payload_with_options()
        return product_data.copy(), ProductService.create_product(**product_data)

    @classmethod
    def populate_product(cls):
        product_data = cls.get_payload()
        return product_data.copy(), ProductService.create_product(**product_data)

    @classmethod
    def populate_demo_products(cls):
        for product in range(2):
            cls.populate_product()

        for product in range(2):
            # TODO populate product with random options
            cls.populate_product_with_options()

    @classmethod
    def populate_active_product(cls):
        payload = {
            "product_name": "test",
            "status": "active",
            "price": cls.get_random_price(),
            "stock": cls.get_random_stock(),
            "options": [],
        }
        return ProductService.create_product(**payload)

    @classmethod
    def populate_archived_product(cls):
        payload = {
            "product_name": "test",
            "status": "archived",
            "price": cls.get_random_price(),
            "stock": cls.get_random_stock(),
            "options": [],
        }
        return ProductService.create_product(**payload)

    @classmethod
    def populate_draft_product(cls):
        payload = {
            "product_name": "test",
            "status": "draft",
            "price": cls.get_random_price(),
            "stock": cls.get_random_stock(),
            "options": [],
        }
        return ProductService.create_product(**payload)
