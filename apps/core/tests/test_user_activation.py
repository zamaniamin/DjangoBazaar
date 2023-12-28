from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser
from apps.core.services.token_service import TokenService


class UserActivationViewTest(APITestCase):
    def setUp(self):
        self.base_url = '/auth/users/'
        self.user_model = get_user_model()

        self.member = FakeUser.populate_user()
        self.member_access_token = TokenService.jwt__get_access_token(self.member)

        self.inactive_user = FakeUser.populate_inactive_user()

    # ----------------------
    # -- test activation ---
    # ----------------------

    def test_user_activation(self):
        """
        Test activating the user after verifying the OTP code (verify email).
        """

        # --- request ---
        payload = {
            "email": self.inactive_user.email,
            "otp": TokenService.create_otp_token()
        }
        response = self.client.patch(self.base_url + 'activation/', payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected['access'], str)
        self.assertIsInstance(expected['refresh'], str)
        self.assertTrue(expected['access'].strip())
        self.assertTrue(expected['refresh'].strip())
        self.assertEqual(expected['message'],
                         'Your email address has been confirmed. Account activated successfully.')

        user = self.user_model.objects.get(email=payload['email'])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_resend_activation_token(self):
        """
        Test resending activation OTP code to email address.
        """

        # --- request ---
        payload = {
            "email": self.member.email
        }
        response = self.client.post(self.base_url + 'resend_activation/', payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- expected email ---
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 3)
        self.assertEqual(expected_mail[2].to, [self.member.email])
