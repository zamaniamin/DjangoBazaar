import json

from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class UpdateProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data that will be shared across all test methods in this class.
        """

        super().setUpTestData()

        # create product
        (
            cls.simple_product_payload,
            cls.simple_product,
        ) = ProductFactory.create_product(get_payload=True)
        (
            cls.variable_product_payload,
            cls.variable_product,
        ) = ProductFactory.create_product(is_variable=True, get_payload=True)

    def setUp(self):
        """
        Set up data or conditions specific to each test method.
        """

        self.set_admin_user_authorization()

    def test_update_by_regular_user(self):
        """Test updating a product by a user (expects HTTP 403 Forbidden)."""

        self.set_regular_user_authorization()
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_by_regular_user(self):
        """Test partially updating a product by a user (expects HTTP 403 Forbidden)."""

        self.set_regular_user_authorization()
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_anonymous_user(self):
        """Test updating a product by a guest (expects HTTP 401 Unauthorized)."""

        self.set_anonymous_user_authorization()
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_by_anonymous_user(self):
        """Test updating a product by a guest (expects HTTP 401 Unauthorized)."""

        self.set_anonymous_user_authorization()
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_required_fields(self):
        """Test updating required fields of a product."""

        payload = {"name": "updated name"}
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["name"], "updated name")

    def test_update_without_required_fields(self):
        """Test updating a product without required fields (expects HTTP 400 Bad Request)."""

        payload = {"description": "updated description"}
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update(self):
        """Test partial updates of a product."""

        payloads = [
            {"name": "partial updated name"},
            {"description": "partial updated description"},
            {"status": Product.STATUS_ARCHIVED},
        ]
        for payload in payloads:
            response = self.client.patch(
                reverse("product-detail", kwargs={"pk": self.simple_product.id}),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            expected = response.json()
            for key, value in payload.items():
                self.assertEqual(expected[key], value)

    def test_partial_update_without_required_fields(self):
        """Test partial update without required fields of a product."""

        payload = {"description": "updated description"}
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["description"], "updated description")

    def test_update_published_after_update_status_to_active(self):
        # create with status draft
        product = ProductFactory.create_product(status=Product.STATUS_DRAFT)

        # update status to active
        payload = {"status": Product.STATUS_ACTIVE}
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": product.id}),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertDatetimeFormat(expected["published_at"])
