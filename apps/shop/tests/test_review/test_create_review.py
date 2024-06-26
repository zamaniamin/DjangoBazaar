from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class CreateAttributeTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_attribute_by_admin(self):
        payload = {
            "attribute_name": "test attribute",
        }
        response = self.client.post(
            path=reverse(viewname="attribute-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_attributes_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(path=reverse(viewname="attribute-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_attributes_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(path=reverse(viewname="attribute-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------------
    # --- Test Create An Attribute ---
    # --------------------------------

    def test_create_attribute(self):
        # request
        payload = {
            "attribute_name": "test attribute",
        }
        response = self.client.post(
            path=reverse(viewname="attribute-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 2)
        self.assertEqual(expected["attribute_name"], payload["attribute_name"])

    def test_create_attribute_if_already_exist(self):
        # create an attribute item
        AttributeFactory.create_attribute()

        # request
        payload = {
            "attribute_name": AttributeFactory.attribute_name,
        }
        response = self.client.post(
            path=reverse(viewname="attribute-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_attribute_if_name_is_empty(self):
        # request
        payload = {"attribute_name": ""}
        response = self.client.post(
            path=reverse(viewname="attribute-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
