import os
import random
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker

from apps.shop.demo.factory.shop_factory_settings import PRODUCTS_COUNT
from apps.shop.models.product import Product
from apps.shop.services.product.product_service import ProductService


class FarsiProductFactory:
    faker = Faker("fa_IR")

    @classmethod
    def create_product(
        cls,
        status: str = Product.STATUS_ACTIVE,
        is_variable: bool = False,
        random_options: bool = False,
        get_payload: bool = False,
        has_images: bool = False,
    ):
        helper = FarsiProductFactoryHelper()

        if is_variable:
            if random_options:
                options = helper.random_options()
            else:
                options = helper.unique_options()
        else:
            options = []

        product_data = {
            "name": " ".join([word.capitalize() for word in cls.faker.words(3)]),
            "description": cls.faker.paragraph(
                nb_sentences=5, variable_nb_sentences=True
            ),
            "status": status,
            "price": helper.random_price(),
            "stock": helper.random_stock(),
            "options": options,
        }
        product = ProductService.create_product(**product_data)

        if has_images:
            images = helper.populate_images(product_id=product.id)
            product_images = ProductService.create_product_images(product.id, **images)
        if get_payload:
            return product_data.copy(), product
        return product

    @classmethod
    def populate_demo_products(cls):
        # -------------------------------------
        # --- populate products with images ---
        # -------------------------------------

        print(f"Adding {13}/{PRODUCTS_COUNT} products with images ... ", end="")

        # active
        for simple_product in range(4):
            cls.create_product(has_images=True)
        for variable_product in range(5):
            cls.create_product(is_variable=True, has_images=True, random_options=True)

        # archived
        cls.create_product(status=Product.STATUS_ARCHIVED, has_images=True)
        cls.create_product(
            status=Product.STATUS_ARCHIVED, is_variable=True, has_images=True
        )

        # draft
        cls.create_product(status=Product.STATUS_DRAFT, has_images=True)
        cls.create_product(
            status=Product.STATUS_DRAFT, is_variable=True, has_images=True
        )
        print("DONE")

        # ----------------------------------------
        # --- populate products without images ---
        # ----------------------------------------

        # print(
        #     f"Adding {PRODUCTS_COUNT - 13}/{PRODUCTS_COUNT} products ... ",
        #     end="",
        # )
        #
        # # archived
        # cls.create_product(status=Product.STATUS_ARCHIVED)
        # cls.create_product(status=Product.STATUS_ARCHIVED, is_variable=True)
        #
        # # draft
        # cls.create_product(status=Product.STATUS_DRAFT)
        # cls.create_product(status=Product.STATUS_DRAFT, is_variable=True)
        #
        # # active
        # for _ in range(PRODUCTS_COUNT - 17):
        #     cls.create_product(
        #         is_variable=random.choice([True, False]),
        #         random_options=random.choice([True, False]),
        #     )
        #
        # print("DONE")


class FarsiProductFactoryHelper:
    options = ["رنگ", "سایز", "جنس", "استایل"]
    option_color_items = ["قرمز", "سبز", "سیاه", "آبی", "زرد"]
    option_size_items = ["S", "M", "L", "XL", "XXL"]
    option_material_items = ["کتان", "نایلون", "پلاستیک", "پشم", "چرم"]
    option_style_items = ["راحتی", "رسمی"]
    product_demo_dir = Path(__file__).resolve().parent.parent.parent / "images/products"

    @staticmethod
    def random_price():
        price1 = round(random.uniform(1, 1000), 2)
        price2 = random.randint(1, 1000)
        return random.choice([price1, price2])

    @staticmethod
    def random_stock():
        return random.randint(1, 100)

    def random_options(self):
        selected_options = random.sample(self.options, random.randint(0, 3))

        # Select items based on the selected options
        if len(selected_options) > 0:
            selected_items = []
            for option in selected_options:
                match option:
                    case "رنگ":
                        option1 = {
                            "option_name": option,
                            "items": random.sample(
                                self.option_color_items, random.randint(1, 5)
                            ),
                        }
                        selected_items.append(option1)

                    case "سایز":
                        option2 = {
                            "option_name": option,
                            "items": random.sample(
                                self.option_size_items, random.randint(1, 5)
                            ),
                        }
                        selected_items.append(option2)
                    case "جنس":
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

    def unique_options(self):
        return [
            {"option_name": "رنگ", "items": self.option_color_items[:2]},
            {"option_name": "سایز", "items": self.option_size_items[:2]},
            {"option_name": "جنس", "items": self.option_material_items[:2]},
        ]

    @classmethod
    def populate_images(cls, product_id):
        """
        Attach some images to a product.

        Read some image file in `.jpg` format from this directory:
        `/apps/shop/demo/images/products/{number}` (you can replace your files in the dir)
        """

        directory_path = os.path.join(
            # because we have 13 dir in the demo products
            cls.product_demo_dir,
            str(min(product_id, 13)),
        )
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
