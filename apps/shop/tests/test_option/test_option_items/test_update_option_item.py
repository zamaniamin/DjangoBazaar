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
        cls.option_name, cls.option_item = OptionFactory.add_one_option_item(cls.option.id)

    def setUp(self):
        self.set_admin_user_authorization()

    def test_update_option_by_admin(self):
        payload = {"item_name": "color"}
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={
                    "option_pk": self.option_name,
                    "pk": self.option_item.option_name_color,
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
                kwargs={"option_pk": self.option_name, "pk": self.option.id},
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
                kwargs={"option_pk": self.option_name, "pk": self.option.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_option_item_if_not_exist(self):
        option_name, option_item = OptionFactory.add_one_option_item(self.option.id)
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={
                    "option_pk": "5a092b03-7920-4c61-ba98-f749296e4750",
                    "pk": option_item.option_name_color,
                },
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_option_item_with_invalid_option_pk(self):
        option_name, option_item = OptionFactory.add_one_option_item(self.option.id)
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": 7, "pk": option_item.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
