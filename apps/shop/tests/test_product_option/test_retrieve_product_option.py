from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class ListProductOptionsTest(ProductBaseTestCase):
    product = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = ProductFactory.create_product(is_variable=True)
        cls.simple_product = ProductFactory.create_product()

    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_list_product_options_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse("product-options-list", kwargs={"product_pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_product_options_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("product-options-list", kwargs={"product_pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_product_options_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse("product-options-list", kwargs={"product_pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ---------------------------------
    # --- Test List Product Options ---
    # ---------------------------------

    def test_list_product_options(self):
        # request
        response = self.client.get(
            reverse("product-options-list", kwargs={"product_pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), 3)
        for option in expected:
            self.assertEqual(
                set(option.keys()),
                {
                    "id",
                    "option_name",
                    "items",
                },
            )

    def test_list_product_options_if_product_not_exist(self):
        response = self.client.get(
            reverse("product-options-list", kwargs={"product_pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_product_options_if_option_not_exist(self):
        response = self.client.get(
            reverse(
                "product-options-list", kwargs={"product_pk": self.simple_product.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), 0)


class RetrieveProductOptionsTest(ProductBaseTestCase):
    product = None
    option_id = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = ProductFactory.create_product(is_variable=True)
        cls.simple_product = ProductFactory.create_product()

    def setUp(self):
        self.set_admin_user_authorization()
        self.option_id = self.get_product_option_id()

    def get_product_option_id(self):
        response = self.client.get(
            reverse("product-options-list", kwargs={"product_pk": self.product.id})
        )

        # expected
        expected = response.json()
        return expected[0]["id"]

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_product_option_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse(
                "product-options-detail",
                kwargs={"product_pk": self.product.id, "pk": self.option_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_option_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse(
                "product-options-detail",
                kwargs={"product_pk": self.product.id, "pk": self.option_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_option_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse(
                "product-options-detail",
                kwargs={"product_pk": self.product.id, "pk": self.option_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------
    # --- Test Retrieve Product Option ---
    # ------------------------------------

    def test_retrieve_product_option(self):
        # request
        response = self.client.get(
            reverse(
                "product-options-detail",
                kwargs={"product_pk": self.product.id, "pk": self.option_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertIsInstance(expected, dict)
        self.assertEqual(len(expected), 3)
        self.assertEqual(
            set(expected.keys()),
            {
                "id",
                "option_name",
                "items",
            },
        )

    def test_retrieve_product_option_if_product_not_exist(self):
        response = self.client.get(
            reverse(
                "product-options-detail",
                kwargs={"product_pk": 999, "pk": self.option_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_product_option_if_option_not_exist(self):
        response = self.client.get(
            reverse(
                "product-options-detail",
                kwargs={"product_pk": self.simple_product.id, "pk": 999},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
