from django.core.management.base import BaseCommand

from apps.core.demo.factory.user_factory import UserFactory


class Command(BaseCommand):
    def handle(self, *args, **options):
        UserFactory.populate_demo_users()
