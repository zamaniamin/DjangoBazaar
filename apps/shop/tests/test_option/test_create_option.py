from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory


class CreateOptionTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_option_by_admin(self):
        payload = {
            "option_name": "test option",
        }
        response = self.client.post(
            path=reverse(viewname="option-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_options_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(path=reverse(viewname="option-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_options_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(path=reverse(viewname="option-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -----------------------------
    # --- Test Create An Option ---
    # -----------------------------

    def test_create_option(self):
        # request
        payload = {
            "option_name": "test option",
        }
        response = self.client.post(
            path=reverse(viewname="option-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 2)
        self.assertEqual(expected["option_name"], payload["option_name"])

    def test_create_option_if_already_exist(self):
        # create an option item
        OptionFactory.create_option()

        # request
        payload = {
            "option_name": OptionFactory.option_name_color,
        }
        response = self.client.post(
            path=reverse(viewname="option-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_option_if_option_name_is_empty(self):
        # request
        payload = {"option_name": ""}
        response = self.client.post(
            path=reverse(viewname="option-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
