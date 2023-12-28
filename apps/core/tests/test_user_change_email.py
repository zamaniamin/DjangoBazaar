from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser
from apps.core.services.token_service import TokenService


class UserChangeEmailViewTest(APITestCase):
    def setUp(self):
        self.base_url = '/auth/users/'
        self.user_model = get_user_model()

        self.member = FakeUser.populate_user()
        self.member_access_token = TokenService.jwt__get_access_token(self.member)

        self.inactive_user = FakeUser.populate_inactive_user()

    # ----------------------
    # -- test activation ---
    # ----------------------

    def test_user_change_email(self):
        """
        Test that the user can change their email.
        """

        # --- request ---
        payload = {
            "email": FakeUser.random_email(),
        }
        response = self.client.post(self.base_url + 'change_email/', payload)

        # --- expected email ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 3)
        self.assertEqual(expected_mail[2].to, [payload['email']])
