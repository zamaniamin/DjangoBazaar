from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.mixin import ProductAssertMixin


class RetrieveVariantTest(APIGetTestCaseMixin, ProductAssertMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = ProductFactory.customize(is_variable=True)
        cls.variant_id = cls.product.variants.first().id

    def api_path(self) -> str:
        return reverse("variants:variant-detail", kwargs={"pk": self.variant_id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertIsInstance(self.response_body, dict)
        self.assertExpectedVariants({"variants": [self.response_body]})

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve_variant(self):
        response = self.send_request()
        self.validate_response_body(response)

    def test_retrieve_if_variant_not_exist(self):
        response = self.send_request(
            reverse("variants:variant-detail", kwargs={"pk": 999})
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)


class ListVariantTest(APIGetTestCaseMixin, ProductAssertMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = ProductFactory.customize(is_variable=True)
        cls.variant_id = cls.product.variants.first().id

    def api_path(self) -> str:
        return reverse("products:product-list-variants", kwargs={"pk": self.product.id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertIsInstance(self.response_body, list)
        for variant in self.response_body:
            self.assertExpectedVariants({"variants": [variant]})

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve(self):
        response = self.send_request()
        self.validate_response_body(response)

    def test_retrieve_if_product_not_exist(self):
        response = self.send_request(
            reverse("products:product-list-variants", kwargs={"pk": 999})
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
