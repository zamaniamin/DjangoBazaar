from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase


class RetrieveProfileBaseTest(CoreBaseTestCase):
    def test_retrieve_profile_by_admin(self):
        # request
        self.set_admin_user_authorization()
        response = self.client.get(reverse("user-me"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "date_joined",
                "last_login",
            },
        )

    def test_retrieve_profile_by_regular_user(self):
        # request
        self.set_regular_user_authorization()
        response = self.client.get(reverse("user-me"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "date_joined",
                "last_login",
            },
        )

    def test_retrieve_profile_by_anonymous_user(self):
        # request
        response = self.client.get(reverse("user-me"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
