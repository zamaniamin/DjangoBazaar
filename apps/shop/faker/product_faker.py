import os
import random
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker

from apps.shop.services.product_service import ProductService


class BaseProductFaker:
    fake = Faker()
    options = ["color", "size", "material", "Style"]
    option_color_items = ["red", "green", "black", "blue", "yellow"]
    option_size_items = ["S", "M", "L", "XL", "XXL"]
    option_material_items = ["Cotton", "Nylon", "Plastic", "Wool", "Leather"]
    option_style_items = ["Casual", "Formal"]

    def __generate_name(self):
        return self.fake.text(max_nb_chars=25)

    def __generate_description(self):
        return self.fake.paragraph(nb_sentences=5)

    @staticmethod
    def __get_random_price():
        return round(random.uniform(1, 100), 2)

    @staticmethod
    def __get_random_stock():
        return random.randint(0, 100)

    def __generate_uniq_options(self):
        return [
            {"option_name": "color", "items": self.option_color_items[:2]},
            {"option_name": "size", "items": self.option_size_items[:2]},
            {"option_name": "material", "items": self.option_material_items[:2]},
        ]

    def __generate_random_options(self):
        selected_options = random.sample(self.options, random.randint(0, 3))

        # Select items based on the selected options
        if len(selected_options) > 0:
            selected_items = []
            for option in selected_options:
                match option:
                    case "color":
                        option1 = {
                            "option_name": option,
                            "items": random.sample(
                                self.option_color_items, random.randint(1, 5)
                            ),
                        }
                        selected_items.append(option1)

                    case "size":
                        option2 = {
                            "option_name": option,
                            "items": random.sample(
                                self.option_size_items, random.randint(1, 5)
                            ),
                        }
                        selected_items.append(option2)
                    case "material":
                        option3 = {
                            "option_name": option,
                            "items": random.sample(
                                self.option_material_items, random.randint(1, 5)
                            ),
                        }
                        selected_items.append(option3)

            return selected_items
        else:
            return []

    def get_payload_status_active(self):
        payload = {
            "product_name": self.__generate_name(),
            "description": self.__generate_description(),
            "status": "active",
            "price": self.__get_random_price(),
            "stock": self.__get_random_stock(),
            "options": [],
        }
        return payload.copy()

    def get_payload_status_archived(self):
        payload = {
            "product_name": "A Archived Product",
            "description": self.__generate_description(),
            "status": "archived",
            "price": self.__get_random_price(),
            "stock": self.__get_random_stock(),
            "options": [],
        }
        return payload.copy()

    def get_payload_status_draft(self):
        payload = {
            "product_name": "A Draft Product",
            "description": self.__generate_description(),
            "status": "draft",
            "price": self.__get_random_price(),
            "stock": self.__get_random_stock(),
            "options": [],
        }
        return payload.copy()

    def get_payload_with_unique_options(self):
        payload = {
            "product_name": self.__generate_name(),
            "description": self.__generate_description(),
            "status": "active",
            "price": self.__get_random_price(),
            "stock": self.__get_random_stock(),
            "options": self.__generate_uniq_options(),
        }
        return payload.copy()

    def get_payload_with_random_options(self):
        payload = {
            "product_name": self.__generate_name(),
            "description": self.__generate_description(),
            "status": "active",
            "price": self.__get_random_price(),
            "stock": self.__get_random_stock(),
            "options": self.__generate_random_options(),
        }
        return payload.copy()


class ProductFaker(BaseProductFaker):
    @classmethod
    def populate_variable_product_by_payload(cls):
        product_data = cls().get_payload_with_unique_options()
        return product_data.copy(), ProductService.create_product(**product_data)

    @classmethod
    def populate_product_by_payload(cls):
        product_data = cls().get_payload_status_active()
        return product_data.copy(), ProductService.create_product(**product_data)

    @classmethod
    def populate_demo_products(cls):
        cls.populate_archived_product()
        cls.populate_draft_product()
        for product in range(2):
            cls.populate_active_product()
        for product in range(2):
            ProductService.create_product(**cls().get_payload_with_random_options())

    @classmethod
    def populate_variable_product(cls):
        return ProductService.create_product(**cls().get_payload_with_unique_options())

    @classmethod
    def populate_active_product(cls):
        return ProductService.create_product(**cls().get_payload_status_active())

    @classmethod
    def populate_active_product_with_image(cls, get_images_object=False):
        product = ProductService.create_product(**cls().get_payload_status_active())
        images = FakeImages.populate_images_for_product(product_id=product.id)
        product_images = ProductService.create_product_images(product.id, **images)
        if get_images_object:
            return product, product_images
        return product

    @classmethod
    def populate_archived_product(cls):
        return ProductService.create_product(**cls().get_payload_status_archived())

    @classmethod
    def populate_draft_product(cls):
        return ProductService.create_product(**cls().get_payload_status_draft())


class FakeImages:
    product_demo_dir = Path(__file__).resolve().parent.parent / "demo/images/products"

    @classmethod
    def populate_images_for_product(cls, product_id):
        """
        Attach some images to a product.

        Read some image file in `.jpg` format from this directory:
        `/apps/shop/demo/images/products/{number}` (you can replace your files in the dir)
        """

        directory_path = os.path.join(cls.product_demo_dir, str(product_id))
        upload = []

        if os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                if filename.endswith(".jpg"):
                    file_path = os.path.join(directory_path, filename)

                    with open(file_path, "rb") as file:
                        file_content = file.read()
                        for_upload = SimpleUploadedFile(
                            name=filename, content=file_content
                        )
                        upload.append(for_upload)

        else:
            raise FileNotFoundError(f"{cls.product_demo_dir}")

        return {"images": upload}
