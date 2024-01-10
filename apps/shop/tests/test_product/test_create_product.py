from rest_framework import status
from rest_framework.utils import json

from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class CreateProductTest(ProductBaseTestCase):
    def setUp(self):
        """
        Set up data or conditions specific to each test method.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

    def test_create_access_as_member(self):
        """
        Test create a product, base on user role, current user is a member.
        - authenticated users.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.member_access_token}")

        # --- request ---
        response = self.client.post(self.product_path, {})

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_access_as_guest(self):
        """
        Test create a product, base on user role, current user is a guest.
        - non-authenticated users.
        """

        # --- request ---
        self.client.credentials()
        response = self.client.post(self.product_path, {})

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
        self.assertIsNone(expected["options"])

        # --- expected product variants ---
        self.assertEqual(len(expected["variants"]), 1)
        self.assertExpectedVariants(
            expected["variants"],
            expected_price=payload["price"],
            expected_stock=payload["stock"],
        )

        # --- expected product media ---
        # TODO add media
        # self.assertIsNone(expected["media"])

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
        # self.assertIsNone(expected["media"])

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    def test_empty_payload(self):
        response = self.client.post(self.product_path, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_required_fields(self):
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
        self.assertIsNone(expected["description"])
        self.assertEqual(expected["status"], "draft")

        # --- expected product date and time ---
        self.assertExpectedDatetimeFormat(expected, published_at=None)

        # --- expected product options ---
        self.assertIsNone(expected["options"])

        # --- expected product variants ---
        self.assertEqual(len(expected["variants"]), 1)
        self.assertExpectedVariants(expected["variants"])

    def test_invalid_required_fields(self):
        """
        Test various scenarios with invalid 'product_name' in the payload during product creation.
        """
        invalid_payloads = [
            {"product_name": ""},
            {"product_name": " "},
            {"product_name": 1},
            {"product_name": []},
            {"product_name": ["d"]},
            {"product_name": ["d", "l"]},
            {"product_name": [{"": 0}]},
            {"product_name": None},
            {"product_name": True},
            {"product_name": False},
            {"product_name": {}},
            {"product_name": ()},
            {"product_name": ("d",)},
            {"product_name": 0},
            {"product_name": 0.0},
            {"product_name": 0j},
            {"product_name": "1" * 256},
        ]
        for payload in invalid_payloads:
            response = self.client.post(
                self.product_path, payload, content_type="application/json"
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_required_fields(self):
        """
        Test case for handling product creation without required fields.
        """
        payload = {
            "description": "test description",
        }
        response = self.client.post(self.product_path, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_status(self):
        """
        Test case for handling valid 'status' values when creating a product.
        """
        invalid_payloads = [
            {"product_name": "Test", "status": "active"},
            {"product_name": "Test", "status": "archived"},
            {"product_name": "Test", "status": "draft"},
            {"product_name": "Test", "status": ""},
            {"product_name": "Test", "status": " "},
            {"product_name": "Test", "status": "1"},
            {"product_name": "Test", "status": "blob"},
            {"product_name": "Test", "status": 1},
        ]
        for payload in invalid_payloads:
            response = self.client.post(self.product_path, payload)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            match payload["status"]:
                case "active":
                    self.assertEqual(response.data["status"], "active")
                case "archived":
                    self.assertEqual(response.data["status"], "archived")
                case "draft":
                    self.assertEqual(response.data["status"], "draft")
                case _:
                    self.assertEqual(response.data["status"], "draft")

    def test_invalid_status(self):
        """
        Test case for handling invalid 'status' values when creating a product.
        """
        invalid_payloads = [
            {"product_name": "Test", "status": None},
            {"product_name": "Test", "status": False},
            {"product_name": "Test", "status": True},
            {"product_name": "Test", "status": []},
        ]

        for payload in invalid_payloads:
            response = self.client.post(
                self.product_path,
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_required_options(self):
        # --- request ---
        payload = {
            "product_name": "Test Product",
            "options": [{"option_name": "color", "items": ["red"]}],
        }
        response = self.client.post(
            self.product_path, json.dumps(payload), content_type="application/json"
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()

        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["product_name"], payload["product_name"])
        self.assertIsNone(expected["description"])
        self.assertEqual(expected["status"], "draft")

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
            "product_name": "test",
            "options": options + [{"option_name": "color", "items": ["black"]}],
        }
        response = self.client.post(
            self.product_path, data=json.dumps(payload), content_type="application/json"
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
            "product_name": "blob",
            "options": [
                {"option_name": "color", "items": ["red", "blue", "red"]},
                {"option_name": "size", "items": ["S", "L"]},
            ],
        }
        response = self.client.post(
            self.product_path, json.dumps(payload), content_type="application/json"
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()

        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["product_name"], payload["product_name"])
        self.assertIsNone(expected["description"])
        self.assertEqual(expected["status"], "draft")

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
            "product_name": "string33",
            "options": [
                {"option_name": "color", "items": ["c"]},
                {"option_name": "material", "items": ["m"]},
                {"option_name": "size", "items": ["s"]},
                {"option_name": "style", "items": []},
            ],
        }
        response = self.client.post(
            self.product_path, data=json.dumps(payload), content_type="application/json"
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
            {"product_name": "test", "options": ""},
            {"product_name": "test", "options": [""]},
            {"product_name": "test", "options": ["blob"]},
            {"product_name": "test", "options": [{}]},
            {"product_name": "test", "options": [{"option_name": []}]},
            {"product_name": "test", "options": [{"option_name": ""}]},
            {"product_name": "test", "options": [{"option_name": "", "items": []}]},
            {"product_name": "test", "options": [{"option_name": "", "items": ["a"]}]},
            {"product_name": "test", "options": [{"option_name": "blob", "items": ""}]},
            # {
            #     "product_name": "test",
            #     "options": [{"option_name": "blob", "items": [1]}],
            # },
            {
                "product_name": "test",
                "options": [{"option_name": "blob", "items_blob": ["a"]}],
            },
            {
                "product_name": "test",
                "options": [{"option_blob": "blob", "items": ["a"]}],
            },
            {
                "product_name": "test",
                "options": [{"items": ["a"], "option_blob": "blob"}],
            },
            {
                "product_name": "test",
                "options": [{"option_name": "blob", "items": [["a", "b"]]}],
            },
        ]
        for payload in invalid_options:
            response = self.client.post(
                self.product_path,
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_price(self):
        """
        Test create a product with invalid price.
        """
        invalid_options = [
            {"product_name": "test", "price": -10},
            {"product_name": "test", "price": None},
            {"product_name": "test", "price": ""},
        ]
        for payload in invalid_options:
            response = self.client.post(
                self.product_path,
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_stock(self):
        """
        Test create a product with invalid stock.
        """
        invalid_options = [
            {"product_name": "test", "stock": -10},
            {"product_name": "test", "stock": None},
            {"product_name": "test", "stock": ""},
            {"product_name": "test", "stock": 1.2},
        ]
        for payload in invalid_options:
            response = self.client.post(
                self.product_path,
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_max_3_options(self):
        """
        Test create a product with more than three options.
        """
        payload = {
            "product_name": "blob",
            "options": [
                {"option_name": "color", "items": ["red"]},
                {"option_name": "size", "items": ["small"]},
                {"option_name": "material", "items": ["x1", "x2"]},
                {"option_name": "blob", "items": ["b"]},
            ],
        }

        response = self.client.post(
            self.product_path, json.dumps(payload), content_type="application/json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
