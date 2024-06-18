import json

from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class UpdateProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
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
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_update_product_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.put(
            path=reverse(
                viewname="product-detail", kwargs={"pk": self.simple_product.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_product_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.patch(
            path=reverse(
                viewname="product-detail", kwargs={"pk": self.simple_product.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.put(
            path=reverse(
                viewname="product-detail", kwargs={"pk": self.simple_product.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_product_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.patch(
            path=reverse(
                viewname="product-detail", kwargs={"pk": self.simple_product.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------
    # --- Test Update Product ---
    # ---------------------------

    def test_update_product_required_fields(self):
        # make request
        payload = {"name": "updated name"}
        response = self.client.put(
            path=reverse(
                viewname="product-detail", kwargs={"pk": self.simple_product.id}
            ),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(expected["name"], "updated name")

    def test_update_product_without_required_fields(self):
        payload = {"description": "updated description"}
        response = self.client.put(
            path=reverse(
                viewname="product-detail", kwargs={"pk": self.simple_product.id}
            ),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_product(self):
        payloads = [
            {"name": "partial updated name"},
            {"description": "partial updated description"},
            {"status": Product.STATUS_ARCHIVED},
        ]
        for payload in payloads:
            response = self.client.patch(
                path=reverse(
                    viewname="product-detail", kwargs={"pk": self.simple_product.id}
                ),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            expected = response.json()
            for key, value in payload.items():
                self.assertEqual(expected[key], value)

    def test_partial_update_product_without_required_fields(self):
        # make request
        payload = {"description": "updated description"}
        response = self.client.patch(
            path=reverse(
                viewname="product-detail", kwargs={"pk": self.simple_product.id}
            ),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(expected["description"], "updated description")

    def test_update_product_published_after_update_status_to_active(self):
        # create with status draft
        product = ProductFactory.create_product(status=Product.STATUS_DRAFT)

        # update status to active
        payload = {"status": Product.STATUS_ACTIVE}
        response = self.client.patch(
            path=reverse(viewname="product-detail", kwargs={"pk": product.id}),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertDatetimeFormat(expected["published_at"])
