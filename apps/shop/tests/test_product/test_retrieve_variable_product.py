from django.urls import reverse

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.mixin import ProductAssertMixin


class RetrieveVariableProductTest(APIGetTestCaseMixin, ProductAssertMixin):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create variable product
        cls.variable_product_payload, cls.variable_product = ProductFactory.customize(
            get_payload=True, is_variable=True, has_attributes=True
        )

    def api_path(self) -> str:
        return reverse(
            "products:product-detail", kwargs={"pk": self.variable_product.id}
        )

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response)
        self.assertExpectedProductResponse(
            self.response_body,
            self.variable_product_payload,
            variants_len=8,
            options_len=3,
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
