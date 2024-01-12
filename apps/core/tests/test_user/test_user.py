from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.faker.user_faker import FakeUser
from apps.core.services.token_service import TokenService


class UserViewTest(APITestCase):
    def setUp(self):
        self.base_url = "/auth/users/"  # TODO use reverse()
        self.me_url = self.base_url + "me/"  # TODO use reverse()

        self.admin = FakeUser.populate_admin()
        self.admin_access_token = TokenService.jwt_get_access_token(self.admin)

        self.member = FakeUser.populate_user()
        self.member_access_token = TokenService.jwt_get_access_token(self.member)

        self.inactive_user = FakeUser.populate_inactive_user()



    # -------------------
    # --- test delete ---
    # -------------------

    def test_delete_user_as_admin(self):
        """
        Test delete a user as an admin.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

        # --- request ---
        response = self.client.delete(f"{self.base_url}{self.member.id}/")

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            get_user_model().objects.get(id=self.member.id)

    def test_delete_user_as_member(self):
        """
        Test patch a user as a member.
        - authenticated users.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.member_access_token}")

        # --- request ---
        response = self.client.delete(f"{self.base_url}{self.member.id}/")

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_as_guest(self):
        """
        Test delete a user as a guest.
        - non-authenticated users.
        """

        # --- request ---
        response = self.client.delete(f"{self.base_url}{self.member.id}/")

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assertDatetimeFormat(self, date):
        formatted_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.assertEqual(date, formatted_date)

    # --------------------
    # --- test read me ---
    # --------------------

    def test_read_me_as_admin(self):
        """
        Test reading current user detail.
        - only authenticated users.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

        # --- request ---
        response = self.client.get(self.me_url)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "date_joined",
                "last_login",
            },
        )

    def test_read_me_as_member(self):
        """
        Test reading current user detail.
        - only authenticated users.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.member_access_token}")

        # --- request ---
        response = self.client.get(self.me_url)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "date_joined",
                "last_login",
            },
        )

    def test_read_me_as_guest(self):
        """
        Test reading current user detail.
        - only authenticated users.
        """

        # --- request ---
        response = self.client.get(self.me_url)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------
    # --- test put me ---
    # -------------------

    def test_put_me_as_admin(self):
        """
        Test putting current user detail.
        - only authenticated users.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

        # --- request ---
        payload = {
            "first_name": "admin f name",
            "last_name": "admin l name",
        }
        response = self.client.put(self.me_url, payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "date_joined",
                "last_login",
            },
        )

    def test_put_me_as_member(self):
        """
        Test putting current user detail.
        - only authenticated users.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.member_access_token}")

        # --- request ---
        payload = {"first_name": "member f name"}
        response = self.client.put(self.me_url, payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "date_joined",
                "last_login",
            },
        )

    def test_put_me_as_guest(self):
        """
        Test putting current user detail.
        - only authenticated users.
        """

        # --- request ---
        response = self.client.put(self.me_url)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------
    # --- test patch me ---
    # ---------------------

    def test_patch_me_as_admin(self):
        """
        Test patch current user detail.
        - only authenticated users.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

        # --- request ---
        payload = {
            "first_name": "admin f name",
            "last_name": "admin l name",
        }
        response = self.client.patch(self.me_url, payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "date_joined",
                "last_login",
            },
        )

    def test_patch_me_as_member(self):
        """
        Test patch current user detail.
        - only authenticated users.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.member_access_token}")

        # --- request ---
        payload = {"first_name": "member f name"}
        response = self.client.patch(self.me_url, payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "date_joined",
                "last_login",
            },
        )

    def test_patch_me_as_guest(self):
        """
        Test patch current user detail.
        - only authenticated users.
        """

        # --- request ---
        response = self.client.patch(self.me_url)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------
    # --- Invalid Payloads ---
    # ------------------------
    # TODO add test for invalid inputs


class JWTTests(APITestCase):
    def setUp(self):
        self.base_url = "/auth/jwt/"  # TODO use reverse()
        self.user = FakeUser.populate_user()

    def test_create_jwt(self):
        """
        Test creating access and refresh tokens.(login)
        """

        # --- request ---
        payload = {"email": self.user.email, "password": FakeUser.password}
        response = self.client.post(self.base_url + "create/", payload)

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertTrue(expected["access"].strip())
        self.assertTrue(expected["refresh"].strip())

    # TODO test JWT refresh
    # TODO test JWT verify
