from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser
from apps.core.services.token_service import TokenService


class CreateProductTest(APITestCase):
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

    def setUp(self):
        """
        Set up data or conditions specific to each test method.
        """

    def test_create_product(self):
        """
        Test create a product by assuming valid data.

        * every time we create product, the media should be None, because the Media after creating a product will be
          attached to it.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.admin_access_token}')

        # --- request ---
        payload = {
            "product_name": "test product",
            "description": "test description",
            "status": "active",
            "price": 11,
            "stock": 11
        }
        response = self.client.post(self.product_path, payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# TODO test access permissions
