from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import BaseCoreTestCase


class RetrieveUserTest(BaseCoreTestCase):
    # ------------------
    # --- list users ---
    # ------------------

    def test_list_users_by_admin(self):
        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        response = self.client.get(reverse("user-list"))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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

    def test_list_users_by_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_by_guest(self):
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------
    # --- retrieve user ---
    # ---------------------

    def test_retrieve_user_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

        # --- request ---
        response = self.client.get(reverse("user-detail",kwargs={"pk":self.regular_user.id}))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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

    def test_retrieve_user_by_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.get(reverse("user-detail",kwargs={"pk":self.regular_user.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_by_guest(self):
        response = self.client.get(reverse("user-detail",kwargs={"pk":self.regular_user.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
