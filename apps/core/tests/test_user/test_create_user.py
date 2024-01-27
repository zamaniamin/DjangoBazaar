import json

from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CreateUserTest(APITestCase):
    def test_create_user_or_register(self):
        """Test that we can create a new user. (register a new user with email and password)"""

        # request
        payload = {
            "email": "user_test@example.com",
            "password": "Test_1234",
            "password_confirm": "Test_1234",
        }
        response = self.client.post(
            reverse("user-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse("password" in response.data)
        self.assertFalse("password_confirm" in response.data)
        self.assertTrue("email" in response.data)
        self.assertTrue("id" in response.data)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        # expected email
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 1)
        self.assertEqual(expected_mail[0].to, [payload["email"]])
