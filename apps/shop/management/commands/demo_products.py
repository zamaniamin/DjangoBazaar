from django.core.management.base import BaseCommand

from apps.shop.demo.factory.product.product_factory import ProductFactory


class Command(BaseCommand):
    def handle(self, *args, **options):
        ProductFactory.populate_demo_products()
