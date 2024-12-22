from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class ListProductsTest(ProductBaseTestCase):
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

    def test_list_product_by_admin(self):
        """
        Test case to list all products by an admin user.

        The test sets the admin user's credentials and then sends a GET request to retrieve the list of all products.
        It asserts that the response status code is HTTP 200 OK, the number of products in the response is 5,
        and each product has a status of "active", "archived", or "draft".
        """

        # request
        self.set_admin_user_authorization()
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(expected["count"], 5)
        expected_products = expected["results"]
        self.assertEqual(len(expected_products), 5)
        for product in expected_products:
            self.assertIn(
                product["status"],
                [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED, Product.STATUS_DRAFT],
            )
            self.assertEqual(
                set(product.keys()),
                {
                    "id",
                    "name",
                    "slug",
                    "description",
                    "status",
                    "options",
                    "variants",
                    "images",
                    "created_at",
                    "updated_at",
                    "published_at",
                },
            )

    def test_list_product_by_regular_user(self):
        """
        Test case to list products by a regular user.

        The test sets the regular user's credentials and then sends a GET request to retrieve the list of products.
        It asserts that the response status code is HTTP 200 OK, the number of products in the response is 4,
        and each product has a status of "active" or "archived", excluding "draft" products.
        """

        # request
        self.set_regular_user_authorization()
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(expected["count"], 4)
        expected_products = expected["results"]
        self.assertEqual(len(expected_products), 4)
        for product in expected_products:
            self.assertNotIn(product["status"], [Product.STATUS_DRAFT])
            self.assertIn(
                product["status"], [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]
            )
            self.assertEqual(
                set(product.keys()),
                {
                    "id",
                    "name",
                    "slug",
                    "description",
                    "status",
                    "options",
                    "variants",
                    "images",
                    "created_at",
                    "updated_at",
                    "published_at",
                },
            )

    def test_list_product_by_anonymous_user(self):
        """
        Test case to list products by a guest user.

        The test resets the client's credentials, simulating a guest user, and then sends a GET request
        to retrieve the list of products. It asserts that the response status code is HTTP 200 OK,
        the number of products in the response is 4, and each product has a status of "active" or "archived",
        excluding "draft" products.
        """

        # request
        self.set_anonymous_user_authorization()
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(expected["count"], 4)
        expected_products = expected["results"]
        self.assertEqual(len(expected_products), 4)
        for product in expected_products:
            self.assertNotIn(product["status"], [Product.STATUS_DRAFT])
            self.assertIn(
                product["status"], [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]
            )

    # -------------------------
    # --- Test List Product ---
    # -------------------------

    def test_list_products_check_product_detail(self):
        """
        Test case to list products and check the structure of each product's details.

        The test resets the client's credentials, simulating a guest user, and then sends a GET request
        to retrieve the list of products. It asserts that the response status code is HTTP 200 OK,
        the number of products in the response is 4, and each product has the expected structure.
        """

        # request
        response = self.client.get(reverse("product-list"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["count"], 4)
        expected_products = expected["results"]
        self.assertEqual(len(expected_products), 4)
        for product in expected_products:
            self.assertEqual(len(product), 11)
            self.assertIn("id", product)
            self.assertIn("name", product)
            self.assertIn("slug", product)
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

        # request
        response = self.client.get(reverse("product-list"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["count"], 0)
        expected_products = expected["results"]
        self.assertEqual(len(expected_products), 0)


class ListDraftProductsTest(APITestCase):
    def test_list_draft_products(self):
        """
        Test case to list draft products.

        The test populates a draft product, sends a GET request to retrieve the list of products,
        and asserts that the response status code is HTTP 200 OK, and the number of products in the response is 0.
        """

        ProductFactory.create_product(status="draft")

        # request
        response = self.client.get(reverse("product-list"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["count"], 0)
        expected_products = expected["results"]
        self.assertEqual(len(expected_products), 0)


class RetrieveProductTest(ProductBaseTestCase):
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

    # -------------------------------
    # --- Test Retrieve A Product ---
    # -------------------------------

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
        self.assertExpectedDatetimeFormat(expected)

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
        self.assertExpectedDatetimeFormat(expected)

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


# TODO test with images
# TODO test with options
# TODO test with variants
# TODO test with categories
# TODO test with attributes

# TODO pagination
# TODO in each pagination should load 12 products
