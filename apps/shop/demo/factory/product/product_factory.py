import os
import random
from pathlib import Path

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify
from faker import Faker

from apps.shop.demo.factory.category.category_factory import CategoryFactory
from apps.shop.models import Product
from apps.shop.services.product_service import ProductService

faker = Faker()


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.LazyAttribute(lambda _: " ".join(faker.words(3)).capitalize())
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name, allow_unicode=True))
    description = factory.Faker("paragraph", nb_sentences=5, variable_nb_sentences=True)
    status = factory.Faker(
        "random_element",
        elements=[Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED, Product.STATUS_DRAFT],
    )
    category = factory.SubFactory(CategoryFactory)

    @factory.lazy_attribute
    def published_at(self):
        return (
            faker.date_time_this_year()
            if self.status == Product.STATUS_ACTIVE
            else None
        )

    @classmethod
    def customize(
        cls,
        is_variable=False,
        has_image=False,
        has_random_options=False,
        get_payload: bool = False,
        count_of_options=3,
        status: str = Product.STATUS_ACTIVE,
        stock: int = -1,
    ):
        category = CategoryFactory()
        product_data = {
            "name": " ".join([word.capitalize() for word in faker.words(3)]),
            "description": faker.paragraph(nb_sentences=5, variable_nb_sentences=True),
            "status": status,
            "price": round(faker.random.uniform(1, 1000), 2),
            "stock": faker.random.randint(1, 100) if stock <= -1 else stock,
            "sku": "123",
            "options": cls._generate_options(
                is_variable, has_random_options, count_of_options
            ),
            "category": category,
        }
        product = ProductService.create_product(**product_data)
        if has_image:
            product = cls._add_images(product)
        if get_payload:
            payload = product_data.copy()
            payload["category"] = category.id
            return payload, product
        return product

    @classmethod
    def _generate_options(cls, is_variable, random_options, count_of_options):
        helper = ProductFactoryHelper()

        if is_variable:
            if random_options:
                return helper.random_options()
            return helper.unique_options(count_of_options)
        return []

    @classmethod
    def _add_images(cls, product):
        """
        Create a product with associated images.
        """
        helper = ProductFactoryHelper()
        images = helper.populate_images(product.id)
        ProductService.create_product_images(product.id, **images)
        return product


class ProductFactoryHelper:
    options = ["color", "size", "material"]
    option_color_items = ["red", "green", "black", "blue", "yellow"]
    option_size_items = ["S", "M", "L", "XL", "XXL"]
    option_material_items = ["Cotton", "Nylon", "Plastic", "Wool", "Leather"]

    @staticmethod
    def random_options():
        selected_options = random.sample(
            ProductFactoryHelper.options, random.randint(0, 3)
        )
        selected_items = []

        for option in selected_options:
            match option:
                case "color":
                    selected_items.append(
                        {
                            "option_name": option,
                            "items": random.sample(
                                ProductFactoryHelper.option_color_items,
                                random.randint(1, 5),
                            ),
                        }
                    )
                case "size":
                    selected_items.append(
                        {
                            "option_name": option,
                            "items": random.sample(
                                ProductFactoryHelper.option_size_items,
                                random.randint(1, 5),
                            ),
                        }
                    )
                case "material":
                    selected_items.append(
                        {
                            "option_name": option,
                            "items": random.sample(
                                ProductFactoryHelper.option_material_items,
                                random.randint(1, 5),
                            ),
                        }
                    )
        return selected_items

    @staticmethod
    def unique_options(count: int = 3):
        options = [
            {
                "option_name": "color",
                "items": ProductFactoryHelper.option_color_items[:2],
            },
            {
                "option_name": "size",
                "items": ProductFactoryHelper.option_size_items[:2],
            },
            {
                "option_name": "material",
                "items": ProductFactoryHelper.option_material_items[:2],
            },
        ]
        return options[:count]

    @classmethod
    def populate_images(cls, product_id):
        """
        Attach images to a product based on its ID.
        """
        # Assuming you have a folder with images named after product IDs
        directory_path = (
            Path(__file__).resolve().parent.parent.parent
            / f"images/products/{min(product_id, 13)}"
        )
        upload = []

        if os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                if filename.endswith(".jpg"):
                    file_path = os.path.join(directory_path, filename)
                    with open(file_path, "rb") as file:
                        file_content = file.read()
                        upload.append(
                            SimpleUploadedFile(name=filename, content=file_content)
                        )

        return {"images": upload}
