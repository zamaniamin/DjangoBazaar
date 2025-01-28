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
        self.assertEqual(len(self.response), 13)
        self.assertIsInstance(self.response["id"], int)
        self.assertEqual(self.response["name"], self.variable_product_payload["name"])

        # TODO add slug
        self.assertEqual(
            self.response["description"], self.variable_product_payload["description"]
        )
        self.assertEqual(
            self.response["status"], self.variable_product_payload["status"]
        )

        # expected product date and time
        self.assertExpectedProductDatetimeFormat(self.response)

        self.assertEqual(
            set(self.response["price"].keys()),
            {"min_price", "max_price"},
        )

        self.assertIsInstance(self.response["total_stock"], int)
        self.assertEqual(len(self.response["options"]), 3)

        # expected product variants
        self.assertEqual(len(self.response["variants"]), 8)
        self.assertExpectedVariants(
            self.response["variants"],
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
