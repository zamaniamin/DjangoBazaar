from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser
from apps.core.models import UserVerification
from apps.core.services.token_service import TokenService


class UserChangeEmailViewTest(APITestCase):
    def setUp(self):
        self.base_url = '/auth/users/me/email/'

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

        # --- init ---
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.member_access_token}')
        new_email = FakeUser.random_email()

        # --- request ---
        payload = {
            "new_email": new_email,
        }
        response = self.client.post(self.base_url, payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- expected email is sent ---
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 3)
        self.assertEqual(expected_mail[2].to, [new_email])

        # --- expected new-email is saved in UserVerification ---
        user = UserVerification.objects.get(user_id=self.member.id)
        self.assertEqual(user.new_email, new_email)

    def test_user_change_email_conformation(self):
        """
        Test user can change their email after conforming the OTP code that sent to their new email address.
        """

        # --- init --
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.member_access_token}')
        new_email = FakeUser.random_email()
        UserVerification.objects.update_or_create(user=self.member, new_email=new_email)

        # --- request ---
        payload = {
            "new_email": new_email,
            "otp": TokenService.create_otp_token()
        }
        response = self.client.post(self.base_url + 'conformation/', payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- expected new email is set ---
        user = get_user_model().objects.get(id=self.member.id)
        self.assertEqual(user.email, new_email)

        # --- expected email is removed from UserVerification ---
        with self.assertRaises(ObjectDoesNotExist):
            UserVerification.objects.get(user_id=self.member.id)
