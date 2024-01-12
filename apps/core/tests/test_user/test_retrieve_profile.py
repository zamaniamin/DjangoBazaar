from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import BaseCoreTestCase


class RetrieveProfileTest(BaseCoreTestCase):
    def test_retrieve_profile_by_admin(self):
        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        response = self.client.get(reverse("user-me"))

        # --- expected ---
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

    def test_retrieve_profile_by_member(self):
        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.get(reverse("user-me"))

        # --- expected ---
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

    def test_retrieve_profile_by_guest(self):
        # --- request ---
        response = self.client.get(reverse("user-me"))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
