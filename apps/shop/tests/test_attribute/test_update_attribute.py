from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class UpdateAttributeTest(CoreBaseTestCase):
    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_attribute()

    def setUp(self):
        self.set_admin_user_authorization()

    def test_update_attribute_by_admin(self):
        # request
        payload = {"name": "black"}
        response = self.client.put(
            reverse(
                "attribute-detail",
                kwargs={"pk": self.attribute.id},
            ),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_attribute_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.put(
            reverse(
                "attribute-detail",
                kwargs={"pk": self.attribute.id},
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_attribute_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.put(
            reverse(
                "attribute-detail",
                kwargs={"pk": self.attribute.id},
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------
    # --- Update attribute ---
    # ---------------------

    def test_update_attribute(self):
        # get old attribute name
        old_attribute_name = self.attribute.name

        # request
        new_attribute_name = "type2"
        payload = {"name": new_attribute_name}
        response = self.client.put(
            reverse(
                "attribute-detail",
                kwargs={"pk": self.attribute.id},
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
                "name",
            },
        )
        self.assertEqual(expected["name"], new_attribute_name)
        self.assertNotEqual(old_attribute_name, new_attribute_name)

    def test_update_attribute_404(self):
        # request
        new_attribute_name = "type2"
        payload = {"attribute_name": new_attribute_name}
        response = self.client.put(
            reverse(
                "attribute-detail",
                kwargs={"pk": 999},
            ),
            json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
