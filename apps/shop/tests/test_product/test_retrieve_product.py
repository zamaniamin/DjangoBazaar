from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.shop.faker.product_faker import ProductFaker
from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class RetrieveProductTest(ProductBaseTestCase):
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

        # --- products with different status ---
        cls.active_product = ProductFaker.populate_active_simple_product()
        cls.archived_product = ProductFaker.populate_archived_simple_product()
        cls.draft_product = ProductFaker.populate_draft_simple_product()

    # ----------------------
    # --- single product ---
    # ----------------------

    def test_retrieve_product(self):
        """
        Test retrieve a product:
        - with product fields.
        - with one variant.
        - no options.
        - no media.
        """

        # --- request ---
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(
            expected["product_name"], self.simple_product_payload["product_name"]
        )
        self.assertEqual(
            expected["description"], self.simple_product_payload["description"]
        )
        self.assertEqual(expected["status"], self.simple_product_payload["status"])

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected)

        # --- expected product options ---
        self.assertIsNone(expected["options"])

        # --- expected product variants ---
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

        # --- request ---
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.variable_product.id})
        )

        # --- expected product ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(
            expected["product_name"], self.variable_product_payload["product_name"]
        )
        self.assertEqual(
            expected["description"], self.variable_product_payload["description"]
        )
        self.assertEqual(expected["status"], self.variable_product_payload["status"])

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected)

        # --- expected product options ---
        self.assertEqual(len(expected["options"]), 3)
        self.assertExpectedOptions(
            expected["options"], self.variable_product_payload["options"]
        )

        # --- expected product variants ---
        self.assertTrue(len(expected["variants"]) == 8)
        self.assertExpectedVariants(
            expected["variants"],
            self.variable_product_payload["price"],
            self.variable_product_payload["stock"],
        )

        # TODO add media assertion

    def test_404(self):
        """
        Test retrieve a product if it doesn't exist.
        """
        response = self.client.get(reverse("product-detail", kwargs={"pk": 999999999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_product_by_admin(self):
        """
        Test case to retrieve product details by an admin user.

        The test sets the admin user's credentials and then sends GET requests for product details
        for each of the active, archived, and draft products. It asserts that the response status code
        is HTTP 200 OK for each request.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

        for product in [self.active_product, self.archived_product, self.draft_product]:
            # --- request ---
            response = self.client.get(
                reverse("product-detail", kwargs={"pk": product.id})
            )

            # --- expected
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_product_by_user(self):
        """
        Test case to retrieve product details by a regular user.

        The test sets the regular user's credentials and then sends GET requests for product details
        for each of the active, archived, and draft products. It asserts that the response status code is
        HTTP 200 OK for active and archived products, and HTTP 404 Not Found for draft products.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")

        for product in [self.active_product, self.archived_product, self.draft_product]:
            # --- request ---
            response = self.client.get(
                reverse("product-detail", kwargs={"pk": product.id})
            )

            # --- expected --
            if product.status in [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            elif product.status == Product.STATUS_DRAFT:
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_product_by_guest(self):
        """
        Test case to retrieve product details by a guest user.

        The test resets the client's credentials, simulating a guest user, and then sends GET requests
        for product details for each of the active, archived, and draft products. It asserts that the
        response status code is HTTP 200 OK for active and archived products, and HTTP 404 Not Found for draft products.
        """
        self.client.credentials()

        for product in [self.active_product, self.archived_product, self.draft_product]:
            # --- request ---
            response = self.client.get(
                reverse("product-detail", kwargs={"pk": product.id})
            )

            # --- expected --
            if product.status in [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            elif product.status == Product.STATUS_DRAFT:
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --------------------
    # --- list product ---
    # --------------------

    def test_list_product_by_admin(self):
        """
        Test case to list all products by an admin user.

        The test sets the admin user's credentials and then sends a GET request to retrieve the list of all products.
        It asserts that the response status code is HTTP 200 OK, the number of products in the response is 5,
        and each product has a status of "active", "archived", or "draft".

        """

        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        response = self.client.get(reverse("product-list"))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 5)
        for product in expected:
            self.assertIn(
                product["status"],
                [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED, Product.STATUS_DRAFT],
            )

    def test_list_product_by_user(self):
        """
        Test case to list products by a regular user.

        The test sets the regular user's credentials and then sends a GET request to retrieve the list of products.
        It asserts that the response status code is HTTP 200 OK, the number of products in the response is 4,
        and each product has a status of "active" or "archived", excluding "draft" products.
        """

        # --- request ---
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.get(reverse("product-list"))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 4)
        for product in expected:
            self.assertNotIn(product["status"], [Product.STATUS_DRAFT])
            self.assertIn(
                product["status"], [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]
            )

    def test_list_product_by_guest(self):
        """
        Test case to list products by a guest user.

        The test resets the client's credentials, simulating a guest user, and then sends a GET request
        to retrieve the list of products. It asserts that the response status code is HTTP 200 OK,
        the number of products in the response is 4, and each product has a status of "active" or "archived",
        excluding "draft" products.
        """

        # --- request ---
        self.client.credentials()
        response = self.client.get(reverse("product-list"))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 4)
        for product in expected:
            self.assertNotIn(product["status"], [Product.STATUS_DRAFT])
            self.assertIn(
                product["status"], [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]
            )

    def test_list_products_check_product_detail(self):
        """
        Test case to list products and check the structure of each product's details.

        The test resets the client's credentials, simulating a guest user, and then sends a GET request
        to retrieve the list of products. It asserts that the response status code is HTTP 200 OK,
        the number of products in the response is 4, and each product has the expected structure.
        """

        # --- request ---
        self.client.credentials()
        response = self.client.get(reverse("product-list"))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 4)
        for product in expected:
            self.assertEqual(len(product), 10)
            self.assertIn("id", product)
            self.assertIn("product_name", product)
            self.assertIn("description", product)
            self.assertIn("status", product)
            self.assertIn("options", product)
            self.assertExpectedVariants(product["variants"])
            # TODO add media assertion
            self.assertDatetimeFormat(product["created_at"])
            self.assertDatetimeFormat(product["updated_at"])
            self.assertIn("published_at", product)


class ListNoProductsTest(APITestCase):
    def test_list_no_products(self):
        """
        Test case for listing products when there are none available.

        The test sends a GET request to retrieve the list of products and asserts that the response status code
        is HTTP 200 OK, and the number of products in the response is 0.
        """

        # --- request ---
        response = self.client.get(reverse("product-list"))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 0)


class ListDraftProductsTest(APITestCase):
    def test_list_draft_products(self):
        """
        Test case to list draft products.

        The test populates a draft product, sends a GET request to retrieve the list of products,
        and asserts that the response status code is HTTP 200 OK, and the number of products in the response is 0.
        """

        ProductFaker.populate_draft_simple_product()

        # --- request ---
        response = self.client.get(reverse("product-list"))

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 0)


# TODO test_with_media
# TODO test_with_options_media

# TODO pagination
# TODO in each pagination should load 12 products
