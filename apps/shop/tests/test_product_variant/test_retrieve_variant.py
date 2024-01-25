from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class RetrieveVariantTest(ProductBaseTestCase):
    product = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.product = ProductFactory.create_product(is_variable=True)
        cls.variant_id = cls.product.variants.first().id

    def test_retrieve_product_variants(self):
        # --- request ---
        response = self.client.get(
            reverse("product-list-variants", kwargs={"pk": self.product.id})
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected, list)
        self.assertExpectedVariants(expected)

    def test_retrieve_product_variants_404(self):
        # --- request ---
        response = self.client.get(reverse("product-list-variants", kwargs={"pk": 11}))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_variant(self):
        # --- request ---
        response = self.client.get(
            reverse("variant-detail", kwargs={"pk": self.variant_id})
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected, dict)
        self.assertExpectedVariants([expected])

    def test_retrieve_variant_404(self):
        # --- request ---
        response = self.client.get(reverse("variant-detail", kwargs={"pk": 1111}))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------
    # --- test access permission ---
    # ------------------------------

    def test_retrieve_product_variant_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse("product-list-variants", kwargs={"pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_variant_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("product-list-variants", kwargs={"pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_variant_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse("product-list-variants", kwargs={"pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_variant_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse("variant-detail", kwargs={"pk": self.variant_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_variant_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("variant-detail", kwargs={"pk": self.variant_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_variant_by_anonymous_user(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse("variant-detail", kwargs={"pk": self.variant_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
