import json

from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.demo.factory.user_factory import UserFactory
from apps.core.models import UserVerification
from apps.core.services.token_service import TokenService


class UserChangeEmailTest(APITestCase):
    def setUp(self):
        self.base_url = "/auth/users/me/change-email/"  # TODO use reverse()

        self.regular_user = UserFactory.create()
        self.regular_user_access_token = TokenService.jwt_get_access_token(
            self.regular_user
        )

    def test_user_change_email(self):
        """Test that the user can change their email."""

        # init
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.regular_user_access_token}")
        new_email = UserFactory.random_email()

        # request
        payload = {
            "new_email": new_email,
        }
        response = self.client.post(
            self.base_url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # expected email is sent
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 2)
        self.assertEqual(expected_mail[1].to, [new_email])

        # expected new-email is saved in UserVerification
        user = UserVerification.objects.get(user_id=self.regular_user.id)
        self.assertEqual(user.new_email, new_email)

    def test_user_change_email_conformation(self):
        """Test user can change their email after conforming the OTP code that sent to their new email address."""

        # init
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.regular_user_access_token}")
        new_email = UserFactory.random_email()
        UserVerification.objects.update_or_create(user=self.regular_user, new_email=new_email)

        # request
        payload = {
            "new_email": new_email,
            "otp": TokenService.create_otp_token(new_email),
        }
        response = self.client.post(
            self.base_url + "conformation/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # expected new email is set
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, new_email)

        # expected email is removed from UserVerification
        with self.assertRaises(ObjectDoesNotExist):
            UserVerification.objects.get(user_id=self.regular_user.id)


# TODO test if user already activated.
# TODO test if the email entered does not match the requested email.
# TODO test with invalid email.
# TODO test with invalid OTP.
# TODO test with invalid expired OTP.
# TODO test user access permission
