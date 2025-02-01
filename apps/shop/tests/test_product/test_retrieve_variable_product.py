from django.urls import reverse

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.mixin import ProductAssertMixin


class RetrieveVariableProductTest(APIGetTestCaseMixin, ProductAssertMixin):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create variable product
        cls.variable_product_payload, cls.variable_product = (
            ProductFactory.create_product(get_payload=True, is_variable=True)
        )

    def api_path(self) -> str:
        return reverse("product-detail", kwargs={"pk": self.variable_product.id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response)
        self.assertEqual(len(self.response_body), 14)
        self.assertIsInstance(self.response_body["id"], int)
        self.assertEqual(
            self.response_body["name"], self.variable_product_payload["name"]
        )

        # TODO add slug
        self.assertEqual(
            self.response_body["description"],
            self.variable_product_payload["description"],
        )
        self.assertEqual(
            self.response_body["status"], self.variable_product_payload["status"]
        )

        # expected product date and time
        self.assertExpectedProductDatetimeFormat(self.response_body)

        self.assertEqual(
            set(self.response_body["price"].keys()),
            {"min_price", "max_price"},
        )

        self.assertIsInstance(self.response_body["total_stock"], int)
        self.assertEqual(len(self.response_body["options"]), 3)

        # expected product variants
        self.assertEqual(len(self.response_body["variants"]), 8)
        self.assertExpectedVariants(
            self.response_body["variants"],
            expected_price=self.variable_product_payload["price"],
            expected_stock=self.variable_product_payload["stock"],
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve(self):
        response = self.send_request()
        self.validate_response_body(response)

    # todo test_retrieve_with_min_price
    # todo test_retrieve_with_max_price
    # todo test_retrieve_with_total_stock
