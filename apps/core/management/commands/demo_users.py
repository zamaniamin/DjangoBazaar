from django.core.management.base import BaseCommand

from apps.core.faker.user_faker import FakeUser


class Command(BaseCommand):
    """
    Custom management command to populate the database with initial data.

    Usage:
        python manage.py demo_users
    """

    help = "Populates the database with initial data"

    def handle(self, *args, **options):
        """
        Handle method to execute the population of demo users.

        Args:
            *args: Additional command-line arguments.
            **options: Additional options.

        """
        FakeUser.populate_demo_users()
