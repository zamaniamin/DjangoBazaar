from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIUpdateTestCaseMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory
from apps.shop.demo.factory.product.product_factory import (
    ProductFactory,
    ProductFactoryHelper,
)
from apps.shop.models.product import Product
from apps.shop.tests.test_product.mixin import ProductAssertMixin


class UpdateVariableProductTest(APIUpdateTestCaseMixin, ProductAssertMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.new_payload = {
            "name": "updated name",
            "slug": "new-slug",
            "description": "updated description",
            "status": Product.STATUS_ARCHIVED,
            "price": 1001,
            "stock": 4002,
            "options": [],
            "category": CategoryFactory().id,
        }
        f_helper = ProductFactoryHelper()

        cls.option = f_helper.unique_options(1)
        cls.new_payload_with_one_option = cls.new_payload.copy()
        cls.new_payload_with_one_option["options"] = [
            {"option_name": "material", "items": ["Cotton"]}
        ]

        cls.options = f_helper.unique_options()
        cls.new_payload_with_multi_options = cls.new_payload.copy()
        cls.new_payload_with_multi_options["options"] = cls.options

    def setUp(self):
        super().setUp()
        (
            self.variable_product_payload,
            self.variable_product,
        ) = ProductFactory.customize(
            is_variable=True, get_payload=True, count_of_options=2
        )

    def api_path(self) -> str:
        return reverse(
            "products:product-detail", kwargs={"pk": self.variable_product.id}
        )

    def validate_response_body(
        self, response, payload, options_len: int = None, variants_len=1
    ):
        super().validate_response_body(response, payload)
        self.assertExpectedProductResponse(
            self.response_body, payload, options_len, variants_len
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_update_with_add_new_option(self):
        response = self.send_request(self.new_payload_with_one_option)
        self.validate_response_body(
            response, self.new_payload_with_one_option, options_len=1
        )

    def test_update_with_required_options(self):
        payload = self.new_payload.copy()
        payload["options"] = [{"option_name": "color", "items": ["red"]}]
        payload["price"] = self.variable_product_payload.get("price")
        payload["stock"] = self.variable_product_payload.get("stock")
        response = self.send_request(payload)
        self.validate_response_body(response, payload, options_len=1)

    def test_update_with_duplicate_options(self):
        options = [
            {"option_name": "color", "items": ["red", "green"]},
            {"option_name": "size", "items": ["S", "M"]},
            {"option_name": "material", "items": ["Cotton", "Nylon"]},
        ]
        final_options = [
            {"option_name": "color", "items": ["red", "green", "black"]},
            {"option_name": "size", "items": ["S", "M"]},
            {"option_name": "material", "items": ["Cotton", "Nylon"]},
        ]
        payload = self.new_payload.copy()
        payload["options"] = options + [{"option_name": "color", "items": ["black"]}]
        payload["price"] = self.variable_product_payload.get("price")
        payload["stock"] = self.variable_product_payload.get("stock")

        response = self.send_request(payload)
        payload["options"] = final_options
        self.validate_response_body(response, payload, options_len=3, variants_len=12)

    def test_update_with_duplicate_items_in_options(self):
        payload = self.new_payload.copy()
        payload["options"] = [
            {"option_name": "color", "items": ["red", "blue", "red"]},
            {"option_name": "size", "items": ["S", "L"]},
        ]
        payload["price"] = self.variable_product_payload.get("price")
        payload["stock"] = self.variable_product_payload.get("stock")
        response = self.send_request(payload)
        self.validate_response_body(response, payload, options_len=2, variants_len=4)

    def test_update_with_invalid_options(self):
        invalid_options = [
            {"name": "test", "options": ""},
            {"name": "test", "options": [""]},
            {"name": "test", "options": ["blob"]},
            {"name": "test", "options": [{}]},
            {"name": "test", "options": [{"option_name": []}]},
            {"name": "test", "options": [{"option_name": ""}]},
            {"name": "test", "options": [{"option_name": "", "items": []}]},
            {"name": "test", "options": [{"option_name": "", "items": ["a"]}]},
            {"name": "test", "options": [{"option_name": "blob", "items": ""}]},
            # {
            #     "name": "test",
            #     "options": [{"option_name": "blob", "items": [1]}],
            # },
            {
                "name": "test",
                "options": [{"option_name": "blob", "items_blob": ["a"]}],
            },
            {
                "name": "test",
                "options": [{"option_blob": "blob", "items": ["a"]}],
            },
            {
                "name": "test",
                "options": [{"items": ["a"], "option_blob": "blob"}],
            },
            {
                "name": "test",
                "options": [{"option_name": "blob", "items": [["a", "b"]]}],
            },
        ]
        for payload in invalid_options:
            response = self.send_request(payload)
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_update_variable_product_with_max_3_options(self):
        payload = {
            "name": "blob",
            "options": [
                {"option_name": "color", "items": ["red"]},
                {"option_name": "size", "items": ["small"]},
                {"option_name": "material", "items": ["x1", "x2"]},
                {"option_name": "blob", "items": ["b"]},
            ],
        }
        response = self.send_request(payload)
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)
