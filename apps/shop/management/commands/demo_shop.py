from django.core.management.base import BaseCommand

from apps.shop.demo.factory.cart.cart_factory import CartFactory
from apps.shop.demo.factory.product.farsi_product_factory import FarsiProductFactory


class Command(BaseCommand):
    def handle(self, *args, **options):
        # ProductFactory.populate_demo_products()
        FarsiProductFactory.populate_demo_products()
        CartFactory.populate_demo_carts()
