from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser
from apps.core.services.token_service import TokenService


class UserResetPasswordViewTest(APITestCase):
    def setUp(self):
        self.base_url = "/auth/users/me/"  # TODO use reverse()

        self.member = FakeUser.populate_user()
        self.member_access_token = TokenService.jwt_get_access_token(self.member)

        self.inactive_user = FakeUser.populate_inactive_user()

    def test_user_reset_password(self):
        """
        Test reset password for a user who is not logged in.
        """

        # --- request ---
        payload = {
            "email": self.member.email,
        }
        response = self.client.post(self.base_url + "reset-password/", payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- expected email is sent ---
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 3)
        self.assertEqual(expected_mail[2].to, [payload["email"]])

    def test_user_reset_password_conformation(self):
        """
        Test user can reset their password after conforming the OTP code that sent to their email address.
        """

        # --- request ---
        payload = {
            "email": self.member.email,
            "otp": TokenService.create_otp_token(self.member.email),
            "new_password": FakeUser.password + "test",
        }
        response = self.client.post(
            self.base_url + "reset-password/conformation/", payload
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- expected new password is set ---
        self.member.refresh_from_db()
        self.assertTrue(self.member.check_password(payload["new_password"]))

    def test_user_change_password(self):
        """
        Test user can change their password.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.member_access_token}")
        cc = self.member.check_password(FakeUser.password)
        # --- request ---
        payload = {
            "current_password": FakeUser.password,
            "new_password": FakeUser.password + "test2",
        }
        response = self.client.post(self.base_url + "change-password/", payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- expected new password is set ---
        self.member.refresh_from_db()
        self.assertTrue(self.member.check_password(payload["new_password"]))


# TODO test logged in users cant reset password, they should use change password
# TODO test access permission on change password
