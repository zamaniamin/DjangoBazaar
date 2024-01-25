import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase


class PartialUpdateProfileTest(CoreBaseTestCase):
    def test_partial_update_by_admin(self):
        # request
        self.set_admin_user_authorization()
        payload = {
            "first_name": "admin f name",
            "last_name": "admin l name",
        }
        response = self.client.patch(
            reverse("user-me"),
            data=json.dumps(payload),
            content_type="application/json",
        )

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

    def test_partial_update_by_regular_user(self):
        # request
        self.set_regular_user_authorization()
        payload = {"first_name": "member f name"}
        response = self.client.patch(
            reverse("user-me"),
            data=json.dumps(payload),
            content_type="application/json",
        )

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

    def test_partial_update_by_anonymous_user(self):
        response = self.client.patch(reverse("user-me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
