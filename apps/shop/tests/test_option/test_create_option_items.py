import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory


class CreateOptionItemsTest(CoreBaseTestCase):
    variable_product = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        self.set_admin_user_authorization()
        self.option = OptionFactory.create_option()
        self.payload = {"item_name": OptionFactory.item_name}

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_option_item_by_admin(self):
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_pk": str(self.option.id)}),
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_option_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_pk": str(self.option.id)}),
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_option_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_pk": str(self.option.id)}),
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------------
    # --- Test Create option Items ---
    # --------------------------------

    def test_create_one_option_item(self):
        # request
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_pk": str(self.option.id)}),
            json.dumps(self.payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["item_name"], str)

    def test_create_one_option_item_if_already_exist(self):
        # create an option item
        OptionFactory.add_one_option_item(self.option.id)

        # request
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_pk": str(self.option.id)}),
            json.dumps(self.payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_one_option_item_if_item_name_is_empty(self):
        # request
        payload = {"item_name": ""}
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_pk": str(self.option.id)}),
            json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
