from django.urls import reverse
from rest_framework import status

from apps.shop.faker.product_faker import ProductFaker
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class RetrieveVariantTest(ProductBaseTestCase):
    product = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.product = ProductFaker.populate_variable_product()
        cls.variant_id = cls.product.productvariant_set.first().id

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
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        response = self.client.get(
            reverse("product-list-variants", kwargs={"pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_variant_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.get(
            reverse("product-list-variants", kwargs={"pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_variant_by_guest(self):
        self.client.credentials()
        response = self.client.get(
            reverse("product-list-variants", kwargs={"pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_variant_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        response = self.client.get(
            reverse("variant-detail", kwargs={"pk": self.variant_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_variant_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.get(
            reverse("variant-detail", kwargs={"pk": self.variant_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_variant_by_guest(self):
        self.client.credentials()
        response = self.client.get(
            reverse("variant-detail", kwargs={"pk": self.variant_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


