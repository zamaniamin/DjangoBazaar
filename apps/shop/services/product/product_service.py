# product_service.py

from apps.shop.models.product import Product
from apps.shop.services.product.product_attributes_manager import ProductAttributeMixin
from apps.shop.services.product.product_data import ProductData
from apps.shop.services.product.product_images_manager import ProductImageMixin
from apps.shop.services.product.product_options_manager import ProductOptionMixin
from apps.shop.services.product.product_repository import ProductRepository
from apps.shop.services.product.product_variants_manager import ProductVariantMixin


class ProductService(
    ProductRepository,
    ProductOptionMixin,
    ProductVariantMixin,
    ProductAttributeMixin,
    ProductImageMixin,
):

    @classmethod
    def create_product(cls, **data) -> Product:
        """High-level method to create a new product."""
        data, product_data = cls._extract_relevant_data(**data)
        product_data.product = Product.objects.create(**data)
        cls.manage_options(product_data)
        cls.manage_variants(product_data)
        cls.manage_attributes(product_data)
        return cls.retrieve_product_details(product_data.product.id)

    @classmethod
    def update_product(cls, product: Product, **data) -> Product:
        """High-level method to update an existing product."""
        data, product_data = cls._extract_relevant_data(**data)
        for attr, value in data.items():
            setattr(product, attr, value)
        product.save()
        product_data.product = product
        cls.manage_options(product_data)
        cls.manage_variants(product_data)
        cls.manage_attributes(product_data)
        return cls.retrieve_product_details(product.id)

    @staticmethod
    def _extract_relevant_data(**data):
        return data, ProductData(
            options=data.pop("options", ProductData.options),
            attributes=data.pop("attributes", ProductData.attributes),
            price=data.pop("price", ProductData.price),
            stock=data.pop("stock", ProductData.stock),
            sku=data.pop("sku", ProductData.sku),
        )


# TODO write tests for sku field on API endpoints
