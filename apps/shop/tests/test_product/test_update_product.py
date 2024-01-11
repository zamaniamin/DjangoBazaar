from django.urls import reverse
from rest_framework import status

from apps.shop.faker.product_faker import FakeProduct
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
        ) = FakeProduct.populate_product()
        (
            cls.variable_product_payload,
            cls.variable_product,
        ) = FakeProduct.populate_product_with_options()

    def setUp(self):
        """
        Set up data or conditions specific to each test method.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

    def test_partial_update(self):
        # --- request ---
        payloads = [
            {"product_name": "updated name"},
            {"description": "updated name"},
            {"status": "archived"},
        ]
        for payload in payloads:
            response = self.client.patch(
                reverse("product-detail", kwargs={"pk": self.simple_product.id}),
                payload,
            )

            # --- expected ---
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            expected = response.json()
            for key, value in payload.items():
                self.assertEqual(expected[key], value)


# TODO test update simple product
# TODO test update variable product
# TODO test partial update
# TODO test access permissions
