from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser
from apps.core.services.token_service import TokenService
from apps.core.tests.base_test import TimeTestCase
from apps.shop.faker.product_faker import FakeProduct


class RetrieveProductTest(APITestCase, TimeTestCase):
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
        cls.product_payload, cls.product = FakeProduct.populate_product_with_options()
        cls.unique_options = FakeProduct.generate_uniq_options()

    def setUp(self):
        """
        Set up data or conditions specific to each test method.
        """

        # self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.admin_access_token}')

    def test_retrieve_product(self):
        """"""
        # --- request ---
        response = self.client.get(f'{self.product_path}{self.product.id}/')

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertTrue('options' in expected)
        for option in expected['options']:
            self.assertTrue('items' in option)
        # TODO write optimized serializers for get the product details as response json that created with POST method
