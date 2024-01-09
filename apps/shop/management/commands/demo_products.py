from django.core.management.base import BaseCommand

from apps.shop.faker.product_faker import FakeProduct


class Command(BaseCommand):
    """
    Custom management command to populate the database with initial data.

    Usage:
        python manage.py demo_products
    """

    help = "Populates the database with initial products data"

    def handle(self, *args, **options):
        """
        Handle method to execute the population of demo products.

        Args:
            *args: Additional command-line arguments.
            **options: Additional options.

        """
        FakeProduct.populate_demo_products()
