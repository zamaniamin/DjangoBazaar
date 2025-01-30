from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status

from apps.core.tests.mixin import APIPostTestCaseMixin
from apps.shop.models import Product
from apps.shop.services.product_service import ProductService
from apps.shop.tests.test_product.mixin import ProductAssertMixin


class CreateProductTest(APIPostTestCaseMixin, ProductAssertMixin):

    def api_path(self) -> str:
        return reverse("product-list")

    def validate_response_body(
        self, response, payload, options_len: int = None, variants_len=1
    ):
        super().validate_response_body(response, payload)

        self.assertIsInstance(self.response_body["id"], int)
        self.assertEqual(self.response_body["name"], payload.get("name"))
        self.assertEqual(self.response_body["description"], payload.get("description"))
        self.assertEqual(
            self.response_body["status"], payload.get("status", Product.STATUS_DRAFT)
        )
        self.assertEqual(
            self.response_body["slug"],
            payload.get("slug", slugify(payload.get("name"), allow_unicode=True)),
        )

        # expected product date and time
        self.assertExpectedProductDatetimeFormat(self.response_body)

        # expected product options
        if options_len:
            self.assertEqual(len(self.response_body["options"]), options_len)
            self.assertExpectedOptions(
                self.response_body["options"], payload.get("options")
            )
        else:
            self.assertIsNone(self.response_body["options"])

        # expected product variants
        self.assertEqual(len(self.response_body["variants"]), variants_len)
        self.assertExpectedVariants(
            self.response_body["variants"],
            expected_price=payload.get("price"),
            expected_stock=payload.get("stock"),
        )

        # expected product media
        self.assertIsNone(self.response_body["images"])

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_create(self):
        """
        Test create a product by assuming valid data.

        * every time we create product, the media should be None, because the Media after creating a product will be
          attached to it.
        """
        payload = {
            "name": "test product",
            "description": "test description",
            "status": Product.STATUS_ACTIVE,
            "price": 11,
            "stock": 11,
            "options": [],
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_create_with_options(self):
        """
        Test create a product with options.
        """
        payload = {
            "name": "test product",
            "description": "test description",
            "status": Product.STATUS_ACTIVE,
            "price": 11,
            "stock": 11,
            "options": [
                {"option_name": "color", "items": ["red", "green"]},
                {"option_name": "size", "items": ["S", "M"]},
                {"option_name": "material", "items": ["Cotton", "Nylon"]},
            ],
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload, options_len=3, variants_len=8)

    def test_create_with_empty_payload(self):
        response = self.send_request({})
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_with_required_fields(self):
        payload = {
            "name": "test product",
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_create_with_invalid_required_fields(self):
        """
        Test various scenarios with invalid 'name' in the payload during product creation.
        """
        invalid_payloads = [
            {"name": ""},
            {"name": " "},
            # {"name": 1},
            {"name": []},
            {"name": ["d"]},
            {"name": ["d", "l"]},
            {"name": [{"": 0}]},
            {"name": None},
            {"name": True},
            {"name": False},
            {"name": {}},
            {"name": ()},
            {"name": ("d",)},
            # {"name": 0},
            # {"name": 0.0},
            # {"name": 0j},
            {"name": "1" * 256},
        ]
        for payload in invalid_payloads:
            response = self.send_request(payload)
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_without_required_fields(self):
        """
        Test case for handling product creation without required fields.
        """
        payload = {
            "description": "test description",
        }
        response = self.send_request(payload)
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_with_valid_status(self):
        """
        Test case for handling valid 'status' values when creating a product.
        """
        invalid_payloads = [
            {"name": "Test", "status": Product.STATUS_ACTIVE},
            {"name": "Test", "status": Product.STATUS_ARCHIVED},
            {"name": "Test", "status": Product.STATUS_DRAFT},
            {"name": "Test", "status": ""},
            {"name": "Test", "status": " "},
            {"name": "Test", "status": "1"},
            {"name": "Test", "status": "blob"},
            {"name": "Test", "status": 1},
        ]
        for payload in invalid_payloads:
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

    def test_create_with_invalid_status(self):
        """
        Test case for handling invalid 'status' values when creating a product.
        """
        invalid_payloads = [
            {"name": "Test", "status": None},
            {"name": "Test", "status": False},
            {"name": "Test", "status": True},
            {"name": "Test", "status": []},
        ]
        for payload in invalid_payloads:
            response = self.send_request(payload)
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_with_required_options(self):
        payload = {
            "name": "Test Product",
            "options": [{"option_name": "color", "items": ["red"]}],
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload, options_len=1)

    def test_create_with_duplicate_options(self):
        """
        Test case for handling duplicate options when creating a product.
        """
        options = [
            {"option_name": "color", "items": ["red", "green"]},
            {"option_name": "size", "items": ["S", "M"]},
            {"option_name": "material", "items": ["Cotton", "Nylon"]},
        ]
        payload = {
            "name": "test",
            "options": options + [{"option_name": "color", "items": ["black"]}],
        }
        response = self.send_request(payload)
        self.assertHTTPStatusCode(response)

        # expected response body
        expected = response.json()
        self.assertEqual(len(expected["options"]), 3)
        final_options = [
            {"option_name": "color", "items": ["red", "green", "black"]},
            {"option_name": "size", "items": ["S", "M"]},
            {"option_name": "material", "items": ["Cotton", "Nylon"]},
        ]
        self.assertExpectedOptions(expected["options"], final_options)
        self.assertExpectedVariants(expected["variants"])

    def test_create_with_duplicate_items_in_options(self):
        payload = {
            "name": "blob",
            "options": [
                {"option_name": "color", "items": ["red", "blue", "red"]},
                {"option_name": "size", "items": ["S", "L"]},
            ],
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload, options_len=2, variants_len=4)

    def test_create_and_remove_empty_options(self):
        """
        Test Remove options if its "items" is empty list.
        """
        payload = {
            "name": "string33",
            "options": [
                {"option_name": "color", "items": ["c"]},
                {"option_name": "material", "items": ["m"]},
                {"option_name": "size", "items": ["s"]},
                {"option_name": "style", "items": []},
            ],
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload, options_len=3)

    def test_create_with_invalid_options(self):
        """
        Test create a product with:
        - invalid option in the payload
        - invalid option-item in payload
        """
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

    def test_create_with_invalid_price(self):
        invalid_options = [
            {"name": "test", "price": -10},
            {"name": "test", "price": None},
            {"name": "test", "price": ""},
        ]
        for payload in invalid_options:
            response = self.send_request(payload)
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_with_invalid_stock(self):
        invalid_options = [
            {"name": "test", "stock": -10},
            {"name": "test", "stock": None},
            {"name": "test", "stock": ""},
            {"name": "test", "stock": 1.2},
        ]
        for payload in invalid_options:
            response = self.send_request(payload)
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_with_max_3_options(self):
        """
        Test create a product with more than three options.
        """
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
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_check_published_at(self):
        product_data = {
            "name": "test product",
            "status": Product.STATUS_ACTIVE,
            "price": 11,
            "stock": 11,
            "sku": 11,
            "options": [],
        }
        product = ProductService.create_product(**product_data)
        self.assertIsNotNone(product.published_at)

        product_data["status"] = Product.STATUS_DRAFT
        product = ProductService.create_product(**product_data)
        self.assertIsNone(product.published_at)

        product_data["status"] = Product.STATUS_ARCHIVED
        product = ProductService.create_product(**product_data)
        self.assertIsNone(product.published_at)


# TODO test invalid slug
