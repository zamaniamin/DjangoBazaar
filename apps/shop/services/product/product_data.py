from dataclasses import dataclass

from apps.shop.models.product import Product


@dataclass
class ProductData:
    product: Product = None
    price: float = 0.00
    stock: int = 0
    sku: str = ""
    options: list = None
    attributes: list = None
