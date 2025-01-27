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

    # ----------------------
    # --- Helper Methods ---
    # ----------------------

    def send_request(self):
        """Send a GET request to the server and return response."""
        return self.client.get(reverse("product-list"))

    def validate_product_list_response_body(self, response, count):
        # expected status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected response body
        expected = response.json()
        self.assertEqual(expected["count"], count)
        expected_product_list = expected["results"]
        self.assertEqual(len(expected_product_list), count)
        for product in expected_product_list:
            self.assertEqual(len(product), 13)
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
                    "price",
                    "total_stock",
                    "images",
                    "created_at",
                    "updated_at",
                    "published_at",
                },
            )

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_list_by_regular_user(self):
        """
        Test case to list products by a regular user.

        The test sets the regular user's credentials and then sends a GET request to retrieve the list of products.
        It asserts that the response status code is HTTP 200 OK, the number of products in the response is 4,
        and each product has a status of "active" or "archived", excluding "draft" products.
        """
        self.set_regular_user_authorization()
        response = self.send_request()
        self.validate_product_list_response_body(response, 4)

        # expected status
        expected = response.json()
        expected_product_list = expected["results"]
        for product in expected_product_list:
            self.assertNotIn(product["status"], [Product.STATUS_DRAFT])
            self.assertIn(
                product["status"], [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]
            )

    def test_list_by_anonymous_user(self):
        """
        Test case to list products by a guest user.

        The test resets the client's credentials, simulating a guest user, and then sends a GET request
        to retrieve the list of products. It asserts that the response status code is HTTP 200 OK,
        the number of products in the response is 4, and each product has a status of "active" or "archived",
        excluding "draft" products.
        """

        # request
        self.set_anonymous_user_authorization()
        response = self.send_request()
        self.validate_product_list_response_body(response, 4)

        # expected
        expected = response.json()
        expected_product_list = expected["results"]
        for product in expected_product_list:
            self.assertNotIn(product["status"], [Product.STATUS_DRAFT])
            self.assertIn(
                product["status"], [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]
            )

    # -------------------------
    # --- Test List Product ---
    # -------------------------

    def test_list(self):
        self.set_admin_user_authorization()
        response = self.send_request()
        self.validate_product_list_response_body(response, 5)

    def test_list_check_product_detail(self):
        """
        Test case to list products and check the structure of each product's details.

        The test resets the client's credentials, simulating a guest user, and then sends a GET request
        to retrieve the list of products. It asserts that the response status code is HTTP 200 OK,
        the number of products in the response is 4, and each product has the expected structure.
        """
        response = self.send_request()
        self.validate_product_list_response_body(response, 4)


class ListNoProductsTest(APITestCase):
    def test_list_no_products(self):
        """
        Test case for listing products when there are none available.

        The test sends a GET request to retrieve the list of products and asserts that the response status code
        is HTTP 200 OK, and the number of products in the response is 0.
        """
        response = self.client.get(reverse("product-list"))
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
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["count"], 0)
        expected_products = expected["results"]
        self.assertEqual(len(expected_products), 0)


# TODO test with images
# TODO test with options
# TODO test with variants
# TODO test with categories
# TODO test with attributes

# TODO pagination
# TODO in each pagination should load 12 products
