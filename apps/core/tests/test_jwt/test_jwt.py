import json

from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.demo.factory.user_factory import UserFactory


class JWTTests(APITestCase):
    def setUp(self):
        self.base_url = "/auth/jwt/"
        self.user = UserFactory.create()

    def test_create_jwt(self):
        """Test creating access and refresh tokens.(login)"""

        # request
        payload = {"email": self.user.email, "password": UserFactory.demo_password()}
        response = self.client.post(
            self.base_url + "create/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertTrue(expected["access"].strip())
        self.assertTrue(expected["refresh"].strip())
