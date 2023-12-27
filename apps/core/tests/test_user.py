from datetime import datetime

from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser
from apps.core.services.token_service import TokenService


class UserViewTest(APITestCase):
    def setUp(self):
        self.base_url = '/auth/users/'
        self.user_model = get_user_model()

        self.admin = FakeUser.populate_admin()
        self.admin_access_token = TokenService.jwt__get_access_token(self.admin)

        self.user = FakeUser.populate_user()
        self.inactive_user = FakeUser.populate_inactive_user()

    def test_create_user_or_register(self):
        """
        Test that we can create a new user.
        (register a new user with email and password)
        """

        # --- request ---
        payload = {
            "email": "user_test@example.com",
            "password": "Test_1234",
            "password_confirm": "Test_1234",
        }
        response = self.client.post(self.base_url, payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse('password' in response.data)
        self.assertFalse('password_confirm' in response.data)
        self.assertTrue('email' in response.data)
        self.assertTrue('user_id' in response.data)
        user = self.user_model.objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        # --- expected email ---
        expected_mail = mail.outbox
        self.assertEqual(len(expected_mail), 4)
        self.assertEqual(expected_mail[3].to, [payload['email']])

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

    def test_list_users_as_admin(self):
        """
        Test listing all users, base on user role, current user is admin.
        - Restrict listing, retrieving, updating, and deleting to admin users only.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.admin_access_token}')

        # --- request ---
        response = self.client.get(self.base_url)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 3)
        for user in expected:
            self.assertEqual(len(user), 7)
            self.assertIsInstance(user['id'], int)
            self.assertIsInstance(user['email'], str)
            self.assertIsInstance(user['first_name'], str)
            self.assertIsInstance(user['last_name'], str)
            self.assertIsInstance(user['is_active'], bool)
            self.assertDatetimeFormat(user['date_joined_formatted'])
            self.assertTrue(
                user['last_login_formatted'] is None or self.assertDatetimeFormat(user['last_login_formatted']))

    def test_list_users_as_member(self):
        """
        Test listing all users, base on user role, current user is a member.
        - authenticated users.
        """

    def test_list_users_as_guest(self):
        """
        Test listing all users, base on user role, current user is a guest.
        - non-authenticated users.
        """

    # TODO test put user
    # TODO test patch user
    # TODO test delete user

    # ------------------------
    # --- Invalid Payloads ---
    # ------------------------

    def assertDatetimeFormat(self, date):
        formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        self.assertEqual(date, formatted_date)


class JWTTests(APITestCase):
    def setUp(self):
        self.base_url = '/auth/jwt/'
        self.user = FakeUser.populate_user()

    def test_create_jwt(self):
        """
        Test creating access and refresh tokens.(login)
        """

        # --- request ---
        payload = {
            "email": self.user.email,
            "password": FakeUser.password
        }
        response = self.client.post(self.base_url + "create/", payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertTrue(expected['access'].strip())
        self.assertTrue(expected['refresh'].strip())

    # TODO test JWT refresh
    # TODO test JWT verify
