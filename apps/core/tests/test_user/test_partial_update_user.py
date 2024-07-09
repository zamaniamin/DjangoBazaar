import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase


class UpdateUserTest(CoreBaseTestCase):
    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_partial_update_user_by_admin(self):
        # request
        self.set_admin_user_authorization()
        payload = {"first_name": "test F name"}
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": self.regular_user.id}),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 7)
        self.assertEqual(expected["id"], self.regular_user.id)
        self.assertEqual(expected["email"], self.regular_user.email)
        self.assertEqual(expected["first_name"], payload["first_name"])
        self.assertEqual(expected["last_name"], self.regular_user.last_name)
        self.assertEqual(expected["is_active"], self.regular_user.is_active)
        self.assertDatetimeFormat(expected["date_joined"])
        self.assertTrue(
            expected["last_login"] is None
            or self.assertDatetimeFormat(expected["last_login"])
        )

    def test_partial_update_user_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_user_by_anonymous_user(self):
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
