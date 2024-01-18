import json

from django.urls import reverse
from rest_framework import status

from apps.shop.faker.product_faker import ProductFaker
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class UpdateProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up data that will be shared across all test methods in this class.
        """

        super().setUpTestData()

        # --- create product ---
        (
            cls.simple_product_payload,
            cls.simple_product,
        ) = ProductFaker.populate_active_simple_product(get_payload=True)
        (
            cls.variable_product_payload,
            cls.variable_product,
        ) = ProductFaker.populate_unique_variable_product(get_payload=True)

    def setUp(self):
        """
        Set up data or conditions specific to each test method.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

    def test_update_by_user(self):
        """Test updating a product by a user (expects HTTP 403 Forbidden)."""

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_by_user(self):
        """Test partially updating a product by a user (expects HTTP 403 Forbidden)."""

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_guest(self):
        """Test updating a product by a guest (expects HTTP 401 Unauthorized)."""

        self.client.credentials()
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_by_guest(self):
        """Test updating a product by a guest (expects HTTP 401 Unauthorized)."""

        self.client.credentials()
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_required_fields(self):
        """Test updating required fields of a product."""

        payload = {"product_name": "updated name"}
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["product_name"], "updated name")

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
            {"product_name": "partial updated name"},
            {"description": "partial updated description"},
            {"status": "archived"},
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
