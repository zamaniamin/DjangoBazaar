from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase


class ListUserTest(CoreBaseTestCase):
    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_list_users_by_admin(self):
        # request
        self.set_admin_user_authorization()
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 2)
        for user in expected:
            self.assertEqual(len(user), 7)
            self.assertIsInstance(user["id"], int)
            self.assertIsInstance(user["email"], str)
            self.assertIsInstance(user["first_name"], str)
            self.assertIsInstance(user["last_name"], str)
            self.assertIsInstance(user["is_active"], bool)
            self.assertDatetimeFormat(user["date_joined"])
            self.assertTrue(
                user["last_login"] is None
                or self.assertDatetimeFormat(user["last_login"])
            )

    def test_list_users_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_by_anonymous_user(self):
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
