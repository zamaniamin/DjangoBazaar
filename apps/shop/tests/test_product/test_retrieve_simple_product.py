from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product
from apps.shop.tests.test_product.mixin import ProductAssertMixin


class RetrieveSimpleProductTest(APIGetTestCaseMixin, ProductAssertMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create product
        (
            cls.simple_product_payload,
            cls.simple_product,
        ) = ProductFactory.create_product(get_payload=True)

        # products with different status
        cls.active_product = ProductFactory.create_product()
        cls.archived_product = ProductFactory.create_product(
            status=Product.STATUS_ARCHIVED
        )
        cls.draft_product = ProductFactory.create_product(status=Product.STATUS_DRAFT)

    def api_path(self) -> str:
        return reverse("product-detail", kwargs={"pk": self.simple_product.id})

    def validate_response_body(self, response):
        super().validate_response_body(response)

        self.assertIsInstance(self.response["id"], int)
        self.assertEqual(self.response["name"], self.simple_product_payload["name"])
        self.assertEqual(
            self.response["description"], self.simple_product_payload["description"]
        )
        self.assertEqual(self.response["status"], self.simple_product_payload["status"])

        # expected product date and time
        self.assertExpectedProductDatetimeFormat(self.response)

        # expected product options
        self.assertIsNone(self.response["options"])

        # expected product variants
        self.assertEqual(len(self.response["variants"]), 1)
        self.assertExpectedVariants(
            self.response["variants"],
            expected_price=self.simple_product_payload["price"],
            expected_stock=self.simple_product_payload["stock"],
        )

        # TODO add media assertion

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve_by_regular_user(self):
        """
        Test case to retrieve product details by a regular user.

        The test sets the regular user's credentials and then sends GET requests for product details
        for each of the active, archived, and draft products. It asserts that the response status code is
        HTTP 200 OK for active and archived products, and HTTP 404 Not Found for draft products.
        """
        self.authorization_as_regular_user()

        for product in [self.active_product, self.archived_product, self.draft_product]:
            response = self.send_request(
                reverse("product-detail", kwargs={"pk": product.id})
            )
            if product.status in [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]:
                self.expected_status_code(response)
            elif product.status == Product.STATUS_DRAFT:
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_by_anonymous_user(self):
        """
        Test case to retrieve product details by a guest user.

        The test resets the client's credentials, simulating a guest user, and then sends GET requests
        for product details for each of the active, archived, and draft products. It asserts that the
        response status code is HTTP 200 OK for active and archived products, and HTTP 404 Not Found for draft products.
        """
        self.authorization_as_anonymous_user()
        for product in [self.active_product, self.archived_product, self.draft_product]:
            response = self.send_request(
                reverse("product-detail", kwargs={"pk": product.id})
            )
            if product.status in [Product.STATUS_ACTIVE, Product.STATUS_ARCHIVED]:
                self.expected_status_code(response)
            elif product.status == Product.STATUS_DRAFT:
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_product(self):
        """
        Test retrieve a product:
        - with product fields.
        - with one variant.
        - no options.
        - no media.
        """
        response = self.send_request()
        self.validate_response_body(response)

    def test_retrieve_404(self):
        response = self.send_request(reverse("product-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
