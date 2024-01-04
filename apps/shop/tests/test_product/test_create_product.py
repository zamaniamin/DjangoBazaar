from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils import json

from apps.core.faker.user_faker import FakeUser
from apps.core.services.token_service import TokenService
from apps.core.tests.base_test import TimeTestCase
from apps.shop.faker.product_faker import FakeProduct


class CreateProductTest(APITestCase, TimeTestCase):
    product_path = '/products/'
    member = None
    admin = None

    @classmethod
    def setUpTestData(cls):
        """
        Set up data that will be shared across all test methods in this class.
        """

        # --- create users ---
        cls.admin = FakeUser.populate_admin()
        cls.admin_access_token = TokenService.jwt__get_access_token(cls.admin)

        cls.member = FakeUser.populate_user()
        cls.member_access_token = TokenService.jwt__get_access_token(cls.member)

        cls.inactive_user = FakeUser.populate_inactive_user()

        # --- fake product ---
        cls.unique_options = FakeProduct.generate_uniq_options()

    def setUp(self):
        """
        Set up data or conditions specific to each test method.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.admin_access_token}')

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
            "options": ""
        }
        response = self.client.post(self.product_path, payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
                {
                    "option_name": "color",
                    "items": ["red", "green"]
                },
                {
                    "option_name": "size",
                    "items": ["S", "M"]
                },
                {
                    "option_name": "material",
                    "items": ["Cotton", "Nylon"]
                }
            ]
        }
        response = self.client.post(self.product_path, data=json.dumps(payload), content_type='application/json')

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected['product_id'], int)
        self.assertEqual(expected['product_name'], payload['product_name'])
        self.assertEqual(expected['description'], payload['description'])
        self.assertEqual(expected['status'], payload['status'])

        # --- expected options ---
        self.assertIsInstance(expected['options'], list)
        self.assertEqual(len(expected['options']), 3)
        for option in expected['options']:
            self.assertIsInstance(option['option_id'], int)
            self.assertIsInstance(option['option_name'], str)

            # Assert that the 'option_name' exists in the 'option' list
            self.assertTrue(
                any(payload_option['option_name'] == option['option_name'] for payload_option in self.unique_options))

            # --- expected items ---
            self.assertIsInstance(option['items'], list)
            self.assertTrue(len(option['items']) == 2)
            for item in option['items']:
                # Find the corresponding payload option
                payload_option = next((payload_option for payload_option in payload['options'] if
                                       payload_option['option_name'] == option['option_name']), None)

                self.assertIsNotNone(payload_option, f"Option '{option['option_name']}' not found in payload options")

                # Assert item properties
                self.assertIsInstance(item['item_id'], int)
                self.assertIsInstance(item['item_name'], str)

                # Assert item name matches the payload
                self.assertIn(item['item_name'], payload_option['items'],
                              f"Item name '{item['item_name']}' not found in payload items")

        # --- expected date and time ---
        self.assert_datetime_format(expected['created_at'])
        self.assert_datetime_format(expected['updated_at'])
        self.assertTrue(expected['published_at'] is None)

        # --- expected variants ---
        self.assertIsInstance(expected['variants'], list)
        self.assertTrue(len(expected['variants']) == 8)
        for variant in expected['variants']:
            self.assertIsInstance(variant['variant_id'], int)
            self.assertIsInstance(variant['product_id'], int)
            self.assertIsInstance(variant['price'], float)
            self.assertEqual(variant['price'], 11)
            self.assertEqual(variant['stock'], 11)
            self.assertIsInstance(variant['option1'], str)
            self.assertIsInstance(variant['option2'], str)
            self.assertIsInstance(variant['option3'], str)
            self.assert_datetime_format(variant['created_at'])
            self.assert_datetime_format(variant['updated_at'])

        # --- expected media ---

    # def out_response(self, data):
    #     for data, value in data.items():
    #         print(data, ":", value)

    def test_create_product_required_fields(self):
        """
        Test create a product with required fields.
        """

        # --- request ---
        payload = {
            "product_name": "test product",
        }
        response = self.client.post(self.product_path, payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# TODO test access permissions
