from django.core.management.base import BaseCommand

from apps.core.faker.user_faker import FakeUser


class Command(BaseCommand):
    """
    usage: python manage.py demo_users
    """
    help = 'Populates the database with initial data'

    def handle(self, *args, **options):
        FakeUser.populate_demo_users()
