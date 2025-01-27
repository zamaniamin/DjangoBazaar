from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import APITestCaseMixin


class RetrieveUserTestMixin(APITestCaseMixin):
    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_user_by_admin(self):
        self.set_admin_user_authorization()

        # request
        response = self.client.get(
            reverse("user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 7)
        self.assertIsInstance(expected["id"], int)
        self.assertIsInstance(expected["email"], str)
        self.assertIsInstance(expected["first_name"], str)
        self.assertIsInstance(expected["last_name"], str)
        self.assertIsInstance(expected["is_active"], bool)
        self.assertDatetimeFormat(expected["date_joined"])
        self.assertTrue(
            expected["last_login"] is None
            or self.assertDatetimeFormat(expected["last_login"])
        )

    def test_retrieve_user_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_by_anonymous_user(self):
        response = self.client.get(
            reverse("user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
