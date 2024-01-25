from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json

from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class CreateProductTest(ProductBaseTestCase):
    def setUp(self):
        """
        Set up data or conditions specific to each test method.
        """

        self.set_admin_user_authorization()

    def test_create_access_as_member(self):
        """
        Test create a product, base on user role, current user is a member.
        - authenticated users.
        """

        self.set_regular_user_authorization()

        # --- request ---
        response = self.client.post(reverse("product-list"), {})

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_access_as_guest(self):
        """
        Test create a product, base on user role, current user is a guest.
        - non-authenticated users.
        """

        # --- request ---
        self.set_anonymous_user_authorization()
        response = self.client.post(reverse("product-list"), {})

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product(self):
        """
        Test create a product by assuming valid data.

        * every time we create product, the media should be None, because the Media after creating a product will be
          attached to it.
        """

        # --- request ---
        payload = {
            "name": "test product",
            "description": "test description",
            "status": Product.STATUS_ACTIVE,
            "price": 11,
            "stock": 11,
            "options": [],
        }
        response = self.client.post(
            reverse("product-list"),
            json.dumps(payload),
            content_type="application/json",
        )

        # --- expected product ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(expected["description"], payload["description"])
        self.assertEqual(expected["status"], payload["status"])

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected)

        # --- expected product options ---
        self.assertIsNone(expected["options"])

        # --- expected product variants ---
        self.assertEqual(len(expected["variants"]), 1)
        self.assertExpectedVariants(
            expected["variants"],
            expected_price=payload["price"],
            expected_stock=payload["stock"],
        )

        # --- expected product media ---
        self.assertIsNone(expected["images"])

    def test_create_product_with_options(self):
        """
        Test create a product with options.
        """

        # --- request ---
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
        response = self.client.post(
            reverse("product-list"),
            json.dumps(payload),
            content_type="application/json",
        )

        # --- expected product ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(expected["description"], payload["description"])
        self.assertEqual(expected["status"], payload["status"])

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected)

        # --- expected product options ---
        self.assertIsNotNone(expected["options"])
        self.assertEqual(len(expected["options"]), 3)
        self.assertExpectedOptions(expected["options"], payload["options"])

        # --- expected product variants ---
        self.assertTrue(len(expected["variants"]) == 8)
        self.assertExpectedVariants(
            expected["variants"], payload["price"], payload["stock"]
        )

        # --- expected product media ---
        self.assertIsNone(expected["images"])

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    def test_empty_payload(self):
        response = self.client.post(
            reverse("product-list"), {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_required_fields(self):
        """
        Test create a product with required fields.
        """

        # --- request ---
        payload = {
            "name": "test product",
        }
        response = self.client.post(
            reverse("product-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # --- expected product ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertIsNone(expected["description"])
        self.assertEqual(expected["status"], Product.STATUS_DRAFT)

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected, published_at=None)

        # --- expected product options ---
        self.assertIsNone(expected["options"])

        # --- expected product variants ---
        self.assertEqual(len(expected["variants"]), 1)
        self.assertExpectedVariants(expected["variants"])

    def test_invalid_required_fields(self):
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
            response = self.client.post(
                reverse("product-list"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_required_fields(self):
        """
        Test case for handling product creation without required fields.
        """
        payload = {
            "description": "test description",
        }
        response = self.client.post(
            reverse("product-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_status(self):
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
            response = self.client.post(
                reverse("product-list"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            match payload["status"]:
                case Product.STATUS_ACTIVE:
                    self.assertEqual(response.data["status"], Product.STATUS_ACTIVE)
                case Product.STATUS_ARCHIVED:
                    self.assertEqual(response.data["status"], Product.STATUS_ARCHIVED)
                case Product.STATUS_DRAFT:
                    self.assertEqual(response.data["status"], Product.STATUS_DRAFT)
                case _:
                    self.assertEqual(response.data["status"], Product.STATUS_DRAFT)

    def test_invalid_status(self):
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
            response = self.client.post(
                reverse("product-list"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_required_options(self):
        # --- request ---
        payload = {
            "name": "Test Product",
            "options": [{"option_name": "color", "items": ["red"]}],
        }
        response = self.client.post(
            reverse("product-list"),
            json.dumps(payload),
            content_type="application/json",
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()

        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertIsNone(expected["description"])
        self.assertEqual(expected["status"], Product.STATUS_DRAFT)

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected, published_at=None)

        # --- expected product options ---
        self.assertEqual(len(expected["options"]), 1)
        self.assertExpectedOptions(expected["options"], payload["options"])

        # --- expected product variants ---
        self.assertTrue(len(expected["variants"]) == 1)
        self.assertExpectedVariants(expected["variants"])

    def test_duplicate_options(self):
        """
        Test case for handling duplicate options when creating a product.
        """

        # --- request ---
        options = [
            {"option_name": "color", "items": ["red", "green"]},
            {"option_name": "size", "items": ["S", "M"]},
            {"option_name": "material", "items": ["Cotton", "Nylon"]},
        ]
        payload = {
            "name": "test",
            "options": options + [{"option_name": "color", "items": ["black"]}],
        }
        response = self.client.post(
            reverse("product-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertEqual(len(expected["options"]), 3)
        self.assertExpectedDatetimeFormat(expected, published_at=None)
        final_options = [
            {"option_name": "color", "items": ["red", "green", "black"]},
            {"option_name": "size", "items": ["S", "M"]},
            {"option_name": "material", "items": ["Cotton", "Nylon"]},
        ]
        self.assertExpectedOptions(expected["options"], final_options)
        self.assertExpectedVariants(expected["variants"])

    def test_duplicate_items_in_options(self):
        # --- request ---
        payload = {
            "name": "blob",
            "options": [
                {"option_name": "color", "items": ["red", "blue", "red"]},
                {"option_name": "size", "items": ["S", "L"]},
            ],
        }
        response = self.client.post(
            reverse("product-list"),
            json.dumps(payload),
            content_type="application/json",
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()

        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertIsNone(expected["description"])
        self.assertEqual(expected["status"], Product.STATUS_DRAFT)

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected, published_at=None)

        # --- expected product options ---
        self.assertEqual(len(expected["options"]), 2)
        self.assertExpectedOptions(expected["options"], payload["options"])

        # --- expected product variants ---
        self.assertTrue(len(expected["variants"]) == 4)
        self.assertExpectedVariants(expected["variants"])

    def test_remove_empty_options(self):
        """
        Test Remove options if its "items" is empty list
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
        response = self.client.post(
            reverse("product-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["options"]), 3)

    def test_invalid_options(self):
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
            response = self.client.post(
                reverse("product-list"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_price(self):
        """
        Test create a product with invalid price.
        """
        invalid_options = [
            {"name": "test", "price": -10},
            {"name": "test", "price": None},
            {"name": "test", "price": ""},
        ]
        for payload in invalid_options:
            response = self.client.post(
                reverse("product-list"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_stock(self):
        """
        Test create a product with invalid stock.
        """
        invalid_options = [
            {"name": "test", "stock": -10},
            {"name": "test", "stock": None},
            {"name": "test", "stock": ""},
            {"name": "test", "stock": 1.2},
        ]
        for payload in invalid_options:
            response = self.client.post(
                reverse("product-list"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_max_3_options(self):
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

        response = self.client.post(
            reverse("product-list"),
            json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
