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
        cls.option_name, cls.option_item = OptionFactory.add_one_item(get_item=True)

    def test_update_option_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_name, "pk": self.option_item.option_name},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_option_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_name, "pk": self.option_item.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_option_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_name, "pk": self.option_item.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_option_item_quantity(self):
        new_quantity = self.option_item.quantity + 1
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_name, "pk": self.option_item.option_name},
            ),
            json.dumps({"quantity": new_quantity}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
      
    def test_update_option_item_quantity_bigger_than_stock(self):
        option_name, option_item = OptionFactory.add_one_item(get_item=True, stock=1)

        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": option_name, "pk": option_item.option_name},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_option_item_if_option_not_exist(self):
        option_name, option_item = OptionFactory.add_one_item(get_item=True)
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={
                    "option_pk": "5a092b03-7920-4c61-ba98-f749296e4750",
                    "pk": option_item.option_name,
                },
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_option_item_if_not_exist(self):
        option_name, option_item = OptionFactory.add_one_item(get_item=True)
        response = self.client.patch(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": option_name, "pk": 1111},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_option_item_with_invalid_option_pk(self):
        option_name, option_item = OptionFactory.add_one_item(get_item=True)
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
