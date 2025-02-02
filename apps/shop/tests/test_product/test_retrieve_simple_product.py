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
        ) = ProductFactory.customize(get_payload=True)

        # products with different status
        cls.active_product = ProductFactory.customize()
        cls.archived_product = ProductFactory.customize(status=Product.STATUS_ARCHIVED)
        cls.draft_product = ProductFactory.customize(status=Product.STATUS_DRAFT)

    def api_path(self) -> str:
        return reverse("product-detail", kwargs={"pk": self.simple_product.id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)

        self.assertIsInstance(self.response_body["id"], int)
        self.assertEqual(
            self.response_body["name"], self.simple_product_payload["name"]
        )
        self.assertEqual(
            self.response_body["description"],
            self.simple_product_payload["description"],
        )
        self.assertEqual(
            self.response_body["status"], self.simple_product_payload["status"]
        )
        self.assertEqual(
            self.response_body["category"], self.simple_product_payload.get("category")
        )

        # expected product date and time
        self.assertExpectedProductDatetimeFormat(self.response_body)

        # expected product options
        self.assertIsNone(self.response_body["options"])

        # expected product variants
        self.assertEqual(len(self.response_body["variants"]), 1)
        self.assertExpectedVariants(
            self.response_body["variants"],
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
                self.assertHTTPStatusCode(response)
            elif product.status == Product.STATUS_DRAFT:
                self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

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
                self.assertHTTPStatusCode(response)
            elif product.status == Product.STATUS_DRAFT:
                self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

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
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
