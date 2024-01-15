from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import BaseCoreTestCase


class UpdateUserTest(BaseCoreTestCase):
    # -------------------
    # --- update user ---
    # -------------------

    def test_update_by_admin(self):
        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        payload = {
            "email": self.regular_user.email,
            "first_name": "F name",
            "last_name": "L name",
            "is_active": True,
        }
        response = self.client.put(
            reverse("user-detail", kwargs={"pk": self.regular_user.id}), payload
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 7)
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["email"], payload["email"])
        self.assertEqual(expected["first_name"], payload["first_name"])
        self.assertEqual(expected["last_name"], payload["last_name"])
        self.assertEqual(expected["is_active"], payload["is_active"])
        self.assertDatetimeFormat(expected["date_joined"])
        self.assertTrue(
            expected["last_login"] is None
            or self.assertDatetimeFormat(expected["last_login"])
        )

    def test_update_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.put(
            reverse("user-detail", kwargs={"pk": self.regular_user.id}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_guest(self):
        response = self.client.put(
            reverse("user-detail", kwargs={"pk": self.regular_user.id}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------
    # --- partial update user ---
    # ---------------------------

    def test_partial_update_by_admin(self):
        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        payload = {"first_name": "test F name"}
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": self.regular_user.id}), payload
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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

    def test_partial_update_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": self.regular_user.id}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_by_guest(self):
        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": self.regular_user.id}), {}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)