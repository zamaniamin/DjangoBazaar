from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIUpdateTestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory
from apps.shop.demo.factory.category.category_factory import CategoryFactory
from apps.shop.demo.factory.product.product_factory import (
    ProductFactory,
    ProductFactoryHelper,
)
from apps.shop.models.product import Product
from apps.shop.tests.test_product.mixin import ProductAssertMixin


class UpdateSimpleProductTest(APIUpdateTestCaseMixin, ProductAssertMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # TODO add sku field
        cls.new_payload = {
            "name": "updated name",
            "slug": "new-slug",
            "description": "updated description",
            "status": Product.STATUS_ARCHIVED,
            "category": CategoryFactory().id,
        }

    def setUp(self):
        super().setUp()
        (
            self.simple_product_payload,
            self.simple_product,
        ) = ProductFactory.customize(get_payload=True, has_attributes=True)

    def api_path(self) -> str:
        return reverse("products:product-detail", kwargs={"pk": self.simple_product.id})

    def validate_response_body(
        self,
        response,
        payload,
        options_len: int = None,
        variants_len=1,
        attributes_len: int = None,
    ):
        super().validate_response_body(response, payload)
        self.assertExpectedProductResponse(
            self.response_body, payload, options_len, variants_len, attributes_len
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_update(self):
        """
        If a product variant already exists, its price, stock, and SKU will not be changed.
        To update these fields, you must update the variant through the variants' endpoint.

        If a product variant is new, the provided price, stock, and SKU will be used to create the new variant.
        """
        response = self.send_request(self.new_payload)
        self.validate_response_body(response, self.new_payload)

    def test_update_with_add_new_options(self):
        payload = self.new_payload.copy()
        payload["options"] = ProductFactoryHelper().unique_options()
        payload["price"] = self.simple_product_payload.get("price")
        payload["stock"] = self.simple_product_payload.get("stock")

        response = self.send_request(payload)
        self.validate_response_body(response, payload, options_len=3, variants_len=8)

    def test_update_with_empty_payload(self):
        response = self.send_request()
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_update_with_required_fields(self):
        payload = {"name": self.new_payload.get("name")}
        response = self.send_request(payload)
        self.assertHTTPStatusCode(response)
        expected = response.json()
        self.assertEqual(expected["name"], self.new_payload.get("name"))

    def test_update_without_required_fields(self):
        payload = {"description": self.new_payload.get("description")}
        response = self.send_request(payload)
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_product(self):
        response = self.send_request(
            self.new_payload, reverse("products:product-detail", kwargs={"pk": 999})
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_update_with_valid_status(self):
        payloads = [
            {"name": "Test", "status": Product.STATUS_ACTIVE},
            {"name": "Test", "status": Product.STATUS_ARCHIVED},
            {"name": "Test", "status": Product.STATUS_DRAFT},
            {"name": "Test", "status": ""},
            {"name": "Test", "status": " "},
            {"name": "Test", "status": "1"},
            {"name": "Test", "status": "blob"},
            {"name": "Test", "status": 1},
        ]
        for payload in payloads:
            response = self.send_request(payload)
            self.assertHTTPStatusCode(response)

            match payload["status"]:
                case Product.STATUS_ACTIVE:
                    self.assertEqual(response.data["status"], Product.STATUS_ACTIVE)
                case Product.STATUS_ARCHIVED:
                    self.assertEqual(response.data["status"], Product.STATUS_ARCHIVED)
                case Product.STATUS_DRAFT:
                    self.assertEqual(response.data["status"], Product.STATUS_DRAFT)
                case _:
                    self.assertEqual(response.data["status"], Product.STATUS_DRAFT)

    def test_update_with_invalid_status(self):
        payloads = [
            {"name": "Test", "status": None},
            {"name": "Test", "status": False},
            {"name": "Test", "status": True},
            {"name": "Test", "status": []},
        ]

        for payload in payloads:
            response = self.send_request(payload)
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_update_with_invalid_price(self):
        invalid_options = [
            {"name": "test", "price": -10},
            {"name": "test", "price": None},
            {"name": "test", "price": ""},
        ]
        for payload in invalid_options:
            response = self.send_request(payload)
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_update_with_invalid_stock(self):
        invalid_options = [
            {"name": "test", "stock": -10},
            {"name": "test", "stock": None},
            {"name": "test", "stock": ""},
            {"name": "test", "stock": 1.2},
        ]
        for payload in invalid_options:
            response = self.send_request(payload)
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_update_add_new_attributes(self):
        new_attributes = AttributeFactory.generate_multiple(get_payload=True)[0]
        self.new_payload["attributes"] = new_attributes
        response = self.send_request(self.new_payload)
        self.validate_response_body(response, self.new_payload, attributes_len=2)


# TODO test update if old attributes was unchecked from product attributes
# TODO test update if new attached attribute-item has same attribute-id
# TODO test_update_check_updated_at
# TODO test update with invalid slug
