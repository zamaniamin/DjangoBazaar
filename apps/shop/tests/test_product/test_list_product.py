from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models.product import Product


class ListProductsTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create products
        (
            cls.simple_product_payload,
            cls.simple_product,
        ) = ProductFactory.customize(get_payload=True)
        (
            cls.variable_product_payload,
            cls.variable_product,
        ) = ProductFactory.customize(get_payload=True, is_variable=True)

        # products with different status
        cls.active_product = ProductFactory.customize()
        cls.archived_product = ProductFactory.customize(status=Product.STATUS_ARCHIVED)
        cls.draft_product = ProductFactory.customize(status=Product.STATUS_DRAFT)

    def api_path(self) -> str:
        return reverse("product-list")

    def validate_response_body(self, response, count: int = 0):
        super().validate_response_body(response)
        self.assertEqual(self.response_body["count"], count)
        expected_product_list = self.response_body["results"]
        self.assertEqual(len(expected_product_list), count)
        for product in expected_product_list:
            self.assertEqual(len(product), 14)
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
                    "category",
                    "price",
                    "total_stock",
                    "images",
                    "created_at",
                    "updated_at",
                    "published_at",
                },
            )

    def test_access_permission_by_regular_user(self):
        """
        Test case to list products by a regular user.

        The test sets the regular user's credentials and then sends a GET request to retrieve the list of products.
        It asserts that the response status code is HTTP 200 OK, the number of products in the response is 4,
        and each product has a status of "active" or "archived", excluding "draft" products.
        """
        response = self.check_access_permission_by_regular_user()
        expected_product_list = response.json().get("results")
        for product in expected_product_list:
            self.assertNotIn(product["status"], [Product.STATUS_DRAFT])
            self.assertIn(
                product["status"], [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]
            )

    def test_access_permission_by_anonymous_user(self):
        """
        Test case to list products by a guest user.

        The test resets the client's credentials, simulating a guest user, and then sends a GET request
        to retrieve the list of products. It asserts that the response status code is HTTP 200 OK,
        the number of products in the response is 4, and each product has a status of "active" or "archived",
        excluding "draft" products.
        """
        response = self.check_access_permission_by_anonymous_user()
        expected_product_list = response.json().get("results")
        for product in expected_product_list:
            self.assertNotIn(product["status"], [Product.STATUS_DRAFT])
            self.assertIn(
                product["status"], [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]
            )

    def test_list(self):
        response = self.send_request()
        self.validate_response_body(response, 5)

    def test_list_check_product_detail(self):
        """
        Test case to list products and check the structure of each product's details.

        The test resets the client's credentials, simulating a guest user, and then sends a GET request
        to retrieve the list of products. It asserts that the response status code is HTTP 200 OK,
        the number of products in the response is 4, and each product has the expected structure.
        """
        response = self.send_request()
        self.validate_response_body(response, 5)


class ListNoProductsTest(APIGetTestCaseMixin):
    def api_path(self) -> str:
        return reverse("product-list")

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response)
        self.assertEqual(self.response_body["count"], 0)
        expected_products = self.response_body["results"]
        self.assertEqual(len(expected_products), 0)

    def test_access_permission_by_regular_user(self):
        response = self.check_access_permission_by_regular_user()
        self.validate_response_body(response)

    def test_access_permission_by_anonymous_user(self):
        response = self.check_access_permission_by_anonymous_user()
        self.validate_response_body(response)

    def test_list_no_products(self):
        response = self.send_request()
        self.validate_response_body(response)


class ListDraftProductsTest(APITestCase):
    def test_list_draft_products(self):
        """
        Test case to list draft products.

        The test populates a draft product, sends a GET request to retrieve the list of products,
        and asserts that the response status code is HTTP 200 OK, and the number of products in the response is 0.
        """
        ProductFactory.customize(status=Product.STATUS_DRAFT)
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
