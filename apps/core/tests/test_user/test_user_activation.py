import json

from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.demo.factory.user_factory import UserFactory
from apps.core.services.token_service import TokenService


class UserActivationTest(APITestCase):
    def setUp(self):
        self.inactive_user = UserFactory.create(is_active=False)

    def test_user_activation(self):
        """Test activating the user after verifying the OTP code (verify email)."""

        # request
        payload = {
            "email": self.inactive_user.email,
            "otp": TokenService.create_otp_token(self.inactive_user.email),
        }
        response = self.client.patch(
            reverse("user-activation"),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected JWT token
        expected = response.json()
        self.assertIsInstance(expected["access"], str)
        self.assertIsInstance(expected["refresh"], str)
        self.assertTrue(expected["access"].strip())
        self.assertTrue(expected["refresh"].strip())
        self.assertEqual(
            expected["message"],
            "Your email address has been confirmed. Account activated successfully.",
        )

        # expected user
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.is_active)
        self.assertFalse(self.inactive_user.is_staff)
        self.assertFalse(self.inactive_user.is_superuser)

    def test_resend_activation_token(self):
        """Test resending activation OTP code to email address."""

        # request
        payload = {"email": self.inactive_user.email}
        response = self.client.post(
            reverse("user-resend-activation"),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # expected email
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 2)
        self.assertEqual(expected_mail[1].to, [self.inactive_user.email])
