from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser


class JWTTests(APITestCase):
    def setUp(self):
        self.base_url = "/auth/jwt/"
        self.user = FakeUser.populate_user()

    def test_create_jwt(self):
        """
        Test creating access and refresh tokens.(login)
        """

        # --- request ---
        payload = {"email": self.user.email, "password": FakeUser.password}
        response = self.client.post(self.base_url + "create/", payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertTrue(expected["access"].strip())
        self.assertTrue(expected["refresh"].strip())
