from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json

from apps.core.tests.base_test import CoreBaseTestCase


class CreateOptionTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_options_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_options_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -----------------------------
    # --- Test Create an option ---
    # -----------------------------

    def test_create_option(self):
        # request
        payload = {
            "option_name": "test option",
        }
        response = self.client.post(
            reverse("option-list"), json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertEqual(len(expected), 2)
        self.assertEqual(expected["option_name"], payload["option_name"])
