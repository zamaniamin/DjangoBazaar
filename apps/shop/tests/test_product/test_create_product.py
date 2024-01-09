from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils import json

from apps.core.faker.user_faker import FakeUser
from apps.core.services.token_service import TokenService
from apps.core.tests.base_test import TimeTestCase
from apps.shop.faker.product_faker import FakeProduct


class CreateProductTest(APITestCase, TimeTestCase):
    product_path = "/products/"
    member = None
    admin = None

    @classmethod
    def setUpTestData(cls):
        """
        Set up data that will be shared across all test methods in this class.
        """

        # --- create users ---
        cls.admin = FakeUser.populate_admin()
        cls.admin_access_token = TokenService.jwt_get_access_token(cls.admin)

        cls.member = FakeUser.populate_user()
        cls.member_access_token = TokenService.jwt_get_access_token(cls.member)

        cls.inactive_user = FakeUser.populate_inactive_user()

        # --- fake product ---
        cls.unique_options = FakeProduct.generate_uniq_options()

    def setUp(self):
        """
        Set up data or conditions specific to each test method.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

    def test_create_product(self):
        """
        Test create a product by assuming valid data.

        * every time we create product, the media should be None, because the Media after creating a product will be
          attached to it.
        """

        # --- request ---
        payload = {
            "product_name": "test product",
            "description": "test description",
            "status": "active",
            "price": 11,
            "stock": 11,
            "options": [],
        }
        response = self.client.post(self.product_path, payload)

        # --- expected product ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["product_name"], payload["product_name"])
        self.assertEqual(expected["description"], payload["description"])
        self.assertEqual(expected["status"], payload["status"])

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected)

        # --- expected product options ---
        self.assertEqual(expected["options"], None)

        # --- expected product variants ---
        self.assertEqual(len(expected["variants"]), 1)
        self.assertExpectedVariants(
            expected["variants"],
            expected_price=payload["price"],
            expected_stock=payload["stock"],
            has_options=False,
        )

        # --- expected product media ---
        # TODO add media
        # self.assertEqual(expected["media"], None)

    def test_create_product_with_options(self):
        """
        Test create a product with options.
        """

        # --- request ---
        payload = {
            "product_name": "test product",
            "description": "test description",
            "status": "active",
            "price": 11,
            "stock": 11,
            "options": [
                {"option_name": "color", "items": ["red", "green"]},
                {"option_name": "size", "items": ["S", "M"]},
                {"option_name": "material", "items": ["Cotton", "Nylon"]},
            ],
        }
        response = self.client.post(
            self.product_path, data=json.dumps(payload), content_type="application/json"
        )

        # --- expected product ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["product_name"], payload["product_name"])
        self.assertEqual(expected["description"], payload["description"])
        self.assertEqual(expected["status"], payload["status"])

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected)

        # --- expected product options ---
        self.assertEqual(len(expected["options"]), 3)
        self.assertExpectedOptions(expected["options"], payload["options"])

        # --- expected product variants ---
        self.assertTrue(len(expected["variants"]) == 8)
        self.assertExpectedVariants(
            expected["variants"], payload["price"], payload["stock"]
        )

        # --- expected product media ---
        # TODO add media
        # self.assertEqual(expected["media"], None)

    def assertExpectedOptions(self, expected_options, payload_options):
        """
        Asserts the expected options in the response.
        """

        self.assertIsInstance(expected_options, list)

        for option in expected_options:
            self.assertIsInstance(option["id"], int)
            self.assertIsInstance(option["option_name"], str)

            # Assert that the 'option_name' exists in the 'option' list
            self.assertTrue(
                any(
                    payload_option["option_name"] == option["option_name"]
                    for payload_option in expected_options
                )
            )

            # Expected items
            self.assertIsInstance(option["items"], list)
            self.assertExpectedItems(option, payload_options)

    def assertExpectedItems(self, expected_option, payload_options):
        """
        Asserts the expected items in the response.
        """

        option_name = expected_option["option_name"]
        option_items = expected_option["items"]
        self.assertIsInstance(option_items, list)

        # Iterate through each item in the actual option's 'items'
        for item in option_items:
            # Find the corresponding payload option in the payload_options list
            payload_option = next(
                (
                    payload_option
                    for payload_option in payload_options
                    if payload_option["option_name"] == option_name
                ),
                None,
            )

            # Check if the payload option corresponding to the current item exists
            self.assertIsNotNone(
                payload_option,
                f"Option '{expected_option['option_name']}' not found in payload options",
            )

            # Assert that the item name in the response matches the payload items for the corresponding option
            self.assertIn(
                item,
                payload_option["items"],
                f"Item name '{item}' not found in payload items",
            )

    def assertExpectedVariants(
        self,
        expected_variants,
        expected_price: int | float = None,
        expected_stock: int = None,
        has_options: bool = True,
    ):
        """
        Asserts the expected variants in the response.
        """
        self.assertIsInstance(expected_variants, list)

        for variant in expected_variants:
            self.assertIsInstance(variant["id"], int)

            # --- price ---
            self.assertIsInstance(variant["price"], float)
            if expected_price is not None:
                self.assertEqual(variant["price"], expected_price)

            # --- stock ---
            self.assertIsInstance(variant["stock"], int)
            if expected_stock is not None:
                self.assertEqual(variant["stock"], expected_stock)

            # --- options ---
            if not has_options:
                self.assertEqual(variant["option1"], None)
                self.assertEqual(variant["option2"], None)
                self.assertEqual(variant["option3"], None)
            else:
                self.assertIsInstance(variant["option1"], str)
                self.assertIsInstance(variant["option2"], str)
                self.assertIsInstance(variant["option3"], str)

            # --- datetime ---
            self.assertDatetimeFormat(variant["created_at"])
            self.assertDatetimeFormat(variant["updated_at"])

    def assertExpectedDatetimeFormat(
        self, expected_product, published_at: str | None = ""
    ):
        """
        Asserts the expected format for datetime strings.
        """
        self.assertDatetimeFormat(expected_product["created_at"])
        self.assertDatetimeFormat(expected_product["updated_at"])
        if published_at is not None:
            self.assertDatetimeFormat(expected_product["published_at"])
        else:
            self.assertIs(expected_product["published_at"], None)

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    def test_create_product_required_fields(self):
        """
        Test create a product with required fields.
        """

        # --- request ---
        payload = {
            "product_name": "test product",
        }
        response = self.client.post(self.product_path, payload)

        # --- expected product ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["product_name"], payload["product_name"])
        self.assertEqual(expected["description"], None)
        self.assertEqual(expected["status"], "draft")

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected, published_at=None)

        # --- expected product options ---
        self.assertEqual(expected["options"], None)

        # --- expected product variants ---
        self.assertEqual(len(expected["variants"]), 1)
        self.assertExpectedVariants(
            expected["variants"],
            has_options=False,
        )


# TODO test access permissions
