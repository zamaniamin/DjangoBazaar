import json

from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.demo.factory.user_factory import UserFactory
from apps.core.services.token_service import TokenService


class UserResetPasswordViewTest(APITestCase):
    def setUp(self):
        self.base_url = "/auth/users/me/"  # TODO use reverse()

        self.member = UserFactory.create()
        self.member_access_token = TokenService.jwt_get_access_token(self.member)

    def test_user_reset_password(self):
        # request
        payload = {
            "email": self.member.email,
        }
        response = self.client.post(
            self.base_url + "reset-password/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # expected email is sent
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 2)
        self.assertEqual(expected_mail[1].to, [payload["email"]])

    def test_user_reset_password_conformation(self):
        """Test user can reset their password after conforming the OTP code that sent to their email address."""

        # request
        payload = {
            "email": self.member.email,
            "otp": TokenService.create_otp_token(self.member.email),
            "new_password": UserFactory.demo_password() + "test",
        }
        response = self.client.post(
            self.base_url + "reset-password/conformation/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # expected new password is set
        self.member.refresh_from_db()
        self.assertTrue(self.member.check_password(payload["new_password"]))

    def test_user_change_password(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.member_access_token}")
        demo_password = UserFactory.demo_password()
        cc = self.member.check_password(demo_password)

        # request
        payload = {
            "current_password": demo_password,
            "new_password": demo_password + "test2",
        }
        response = self.client.post(
            self.base_url + "change-password/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # expected new password is set
        self.member.refresh_from_db()
        self.assertTrue(self.member.check_password(payload["new_password"]))


# TODO test logged in users cant reset password, they should use change password
# TODO test access permission on change password
