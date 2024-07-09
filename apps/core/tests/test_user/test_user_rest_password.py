import json

from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.demo.factory.user_factory import UserFactory
from apps.core.services.token_service import TokenService


class UserResetPasswordTest(APITestCase):
    def setUp(self):
        self.regular_user = UserFactory.create()
        self.regular_user_access_token = TokenService.jwt_get_access_token(
            self.regular_user
        )

    def test_user_reset_password(self):
        # request
        payload = {
            "email": self.regular_user.email,
        }
        response = self.client.post(
            reverse("user-reset-password"),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # expected email is sent
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 2)
        self.assertEqual(expected_mail[1].to, [payload["email"]])

    def test_user_reset_password_conformation(self):
        """Test user can reset their password after conforming the OTP code that sent to their email address."""

        # request
        payload = {
            "email": self.regular_user.email,
            "otp": TokenService.create_otp_token(self.regular_user.email),
            "new_password": UserFactory.demo_password() + "test",
        }
        response = self.client.post(
            reverse("user-reset-password-conformation"),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # expected new password is set
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password(payload["new_password"]))

    def test_user_change_password(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"JWT {self.regular_user_access_token}"
        )
        demo_password = UserFactory.demo_password()
        cc = self.regular_user.check_password(demo_password)

        # request
        payload = {
            "current_password": demo_password,
            "new_password": demo_password + "test2",
        }
        response = self.client.post(
            reverse("user-change-password"),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # expected new password is set
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password(payload["new_password"]))


# TODO test logged in users cant reset password, they should use change password
# TODO test access permission on change password
