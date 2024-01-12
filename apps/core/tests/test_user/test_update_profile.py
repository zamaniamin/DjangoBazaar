from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import BaseCoreTestCase


class ProfileTest(BaseCoreTestCase):
    # ----------------------
    # --- Update Profile ---
    # ----------------------

    def test_update_by_admin(self):
        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        payload = {
            "first_name": "admin f name",
            "last_name": "admin l name",
        }
        response = self.client.put(reverse("user-me"), payload)

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

    def test_update_by_member(self):
        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        payload = {"first_name": "member f name"}
        response = self.client.put(reverse("user-me"), payload)

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

    def test_update_by_guest(self):
        response = self.client.put(reverse("user-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------
    # --- Partial Update Profile ---
    # ------------------------------

    def test_partial_update_by_admin(self):
        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        payload = {
            "first_name": "admin f name",
            "last_name": "admin l name",
        }
        response = self.client.patch(reverse("user-me"), payload)

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

    def test_partial_update_by_member(self):
        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        payload = {"first_name": "member f name"}
        response = self.client.patch(reverse("user-me"), payload)

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

    def test_partial_update_by_guest(self):
        response = self.client.patch(reverse("user-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
