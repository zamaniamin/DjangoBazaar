import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory


class UpdateOptionItemTest(CoreBaseTestCase):
    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()
        cls.item = OptionFactory.add_one_option_item(cls.option.id)

    def setUp(self):
        self.set_admin_user_authorization()

    def test_update_option_by_admin(self):
        payload = {"item_name": "color"}
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={
                    "option_pk": self.option.id, "pk": self.item.id
                },
            ),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_option_by_regular_user(self):
        self.set_regular_user_authorization()
        payload = {"item_name": "color"}
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={
                    "option_pk": self.option.id, "pk": self.item.id
                },
            ),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_option_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={
                    "option_pk": self.option.id, "pk": self.item.id
                },
            ),
            json.dumps({"item_name": "color"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_option(self):
        # get old option name
        old_item_name = self.item.item_name

        # request
        new_item_name = "color2"
        payload = {"item_name": new_item_name}
        response = self.client.put(
            reverse(
                "option-items-detail",
                kwargs={
                    "option_pk": self.option.id, "pk": self.item.id
                },
            ),
            json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "item_name",
            },
        )
        self.assertEqual(expected["item_name"], new_item_name)
        self.assertNotEqual(old_item_name, new_item_name)

    def test_update_option_item_404(self):
        # request
        new_item_name = "color2"
        payload = {"item_name": new_item_name}
        response = self.client.put(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": 999},
            ),
            json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_option_item_with_invalid_option_pk(self):
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": 77, "pk": self.item.id},
            ),
            json.dumps({"item_name": "color"}),
            content_type="application/json",
        )
        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
