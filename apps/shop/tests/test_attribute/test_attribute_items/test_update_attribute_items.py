import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class UpdateAttributeItemTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_attribute()
        cls.item = AttributeFactory.add_one_attribute_item(cls.attribute.id)

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_update_item_by_admin(self):
        payload = {"item_name": "new item name"}
        response = self.client.put(
            path=reverse(
                viewname="attribute-items-detail",
                kwargs={"attribute_pk": self.attribute.id, "pk": self.item.id},
            ),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.put(
            path=reverse(
                viewname="attribute-items-detail",
                kwargs={"attribute_pk": self.attribute.id, "pk": self.item.id},
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.put(
            path=reverse(
                viewname="attribute-items-detail",
                kwargs={"attribute_pk": self.attribute.id, "pk": self.item.id},
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------------
    # --- Test Update Items ---
    # -------------------------

    def test_update_item(self):
        # get old item name
        old_item_name = self.item.item_name

        # request
        new_item_name = "item name 2"
        payload = {"item_name": new_item_name}
        response = self.client.put(
            path=reverse(
                viewname="attribute-items-detail",
                kwargs={"attribute_pk": self.attribute.id, "pk": self.item.id},
            ),
            data=json.dumps(payload),
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

    def test_update_with_invalid_item_pk(self):
        # request
        response = self.client.put(
            path=reverse(
                viewname="attribute-items-detail",
                kwargs={"attribute_pk": self.attribute.id, "pk": 999},
            ),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_attribute_item_with_invalid_attribute_pk(self):
        response = self.client.put(
            path=reverse(
                viewname="attribute-items-detail",
                kwargs={"attribute_pk": 99999, "pk": self.item.id},
            ),
            content_type="application/json",
        )
        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
