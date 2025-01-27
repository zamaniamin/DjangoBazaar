from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class RetrieveSimpleProductTest(ProductBaseTestCase):
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
        ) = ProductFactory.create_product(get_payload=True, is_variable=True)

        # products with different status
        cls.active_product = ProductFactory.create_product()
        cls.archived_product = ProductFactory.create_product(
            status=Product.STATUS_ARCHIVED
        )
        cls.draft_product = ProductFactory.create_product(status=Product.STATUS_DRAFT)

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_product_by_admin(self):
        """
        Test case to retrieve product details by an admin user.

        The test sets the admin user's credentials and then sends GET requests for product details
        for each of the active, archived, and draft products. It asserts that the response status code
        is HTTP 200 OK for each request.
        """
        self.set_admin_user_authorization()

        for product in [self.active_product, self.archived_product, self.draft_product]:
            # request
            response = self.client.get(
                reverse("product-detail", kwargs={"pk": product.id})
            )

            # expected
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_by_regular_user(self):
        """
        Test case to retrieve product details by a regular user.

        The test sets the regular user's credentials and then sends GET requests for product details
        for each of the active, archived, and draft products. It asserts that the response status code is
        HTTP 200 OK for active and archived products, and HTTP 404 Not Found for draft products.
        """
        self.set_regular_user_authorization()

        for product in [self.active_product, self.archived_product, self.draft_product]:
            # request
            response = self.client.get(
                reverse("product-detail", kwargs={"pk": product.id})
            )

            # expected
            if product.status in [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            elif product.status == Product.STATUS_DRAFT:
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_product_by_anonymous_user(self):
        """
        Test case to retrieve product details by a guest user.

        The test resets the client's credentials, simulating a guest user, and then sends GET requests
        for product details for each of the active, archived, and draft products. It asserts that the
        response status code is HTTP 200 OK for active and archived products, and HTTP 404 Not Found for draft products.
        """
        self.set_anonymous_user_authorization()

        for product in [self.active_product, self.archived_product, self.draft_product]:
            # request
            response = self.client.get(
                reverse("product-detail", kwargs={"pk": product.id})
            )

            # expected
            if product.status in [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            elif product.status == Product.STATUS_DRAFT:
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --------------------------------------
    # --- Test Retrieve A Simple Product ---
    # --------------------------------------

    def test_retrieve_product(self):
        """
        Test retrieve a product:
        - with product fields.
        - with one variant.
        - no options.
        - no media.
        """

        # request
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], self.simple_product_payload["name"])
        self.assertEqual(
            expected["description"], self.simple_product_payload["description"]
        )
        self.assertEqual(expected["status"], self.simple_product_payload["status"])

        # expected product date and time
        self.assertExpectedProductDatetimeFormat(expected)

        # expected product options
        self.assertIsNone(expected["options"])

        # expected product variants
        self.assertEqual(len(expected["variants"]), 1)
        self.assertExpectedVariants(
            expected["variants"],
            expected_price=self.simple_product_payload["price"],
            expected_stock=self.simple_product_payload["stock"],
        )

        # TODO add media assertion

    def test_retrieve_product_with_options(self):
        """
        Test retrieve a product with options:
        - with price and stock.
        - with options
        - with variants.
        - no media.
        """

        # request
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.variable_product.id})
        )

        # expected product
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], self.variable_product_payload["name"])
        self.assertEqual(
            expected["description"], self.variable_product_payload["description"]
        )
        self.assertEqual(expected["status"], self.variable_product_payload["status"])

        # expected product date and time
        self.assertExpectedProductDatetimeFormat(expected)

        # expected product options
        self.assertEqual(len(expected["options"]), 3)
        self.assertExpectedOptions(
            expected["options"], self.variable_product_payload["options"]
        )

        # expected product variants
        self.assertTrue(len(expected["variants"]) == 8)
        self.assertExpectedVariants(
            expected["variants"],
            self.variable_product_payload["price"],
            self.variable_product_payload["stock"],
        )

        # TODO add media assertion

    def test_retrieve_product_if_not_exist(self):
        response = self.client.get(reverse("product-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
