from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import BaseCoreTestCase


class DestroyUserTest(BaseCoreTestCase):
    def test_delete_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")
        response = self.client.delete(
            reverse("user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            get_user_model().objects.get(id=self.regular_user.id)

    def test_delete_by_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.user_access_token}")
        response = self.client.delete(
            reverse("user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_by_guest(self):
        response = self.client.delete(
            reverse("user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
