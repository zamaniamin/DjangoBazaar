import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APITestCaseMixin


class UpdateProfileTestMixin(APITestCaseMixin):
    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_update_profile_by_admin(self):
        # request
        self.set_admin_user_authorization()
        payload = {
            "first_name": "admin f name",
            "last_name": "admin l name",
        }
        response = self.client.put(
            reverse("user-me"),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "is_staff",
                "date_joined",
                "last_login",
            },
        )

    def test_update_profile_by_regular_user(self):
        # request
        self.set_regular_user_authorization()
        payload = {"first_name": "member f name"}
        response = self.client.put(
            reverse("user-me"),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "is_staff",
                "date_joined",
                "last_login",
            },
        )

    def test_update_profile_by_anonymous_user(self):
        response = self.client.put(reverse("user-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
