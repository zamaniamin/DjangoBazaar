from django.urls import reverse
from rest_framework import status

from apps.shop.faker.product_faker import ProductFaker
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class UpdateVariantTest(ProductBaseTestCase):
    product = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.product = ProductFaker.populate_variable_product()
        cls.variant_id = cls.product.productvariant_set.first().id

    def test_update_variant(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

        # --- request ---
        payload = {
            "price": 11,
            "stock": 111,
        }
        response = self.client.put(
            reverse("variant-detail", kwargs={"pk": self.variant_id}), payload
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["price"], 11)
        self.assertEqual(expected["stock"], 111)


# TODO add partial update too
