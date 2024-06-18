from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase


class DestroyUserTest(CoreBaseTestCase):
    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_delete_user_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.delete(
            path=reverse(viewname="user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            get_user_model().objects.get(id=self.regular_user.id)

    def test_delete_user_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            path=reverse(viewname="user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_by_anonymous_user(self):
        response = self.client.delete(
            path=reverse(viewname="user-detail", kwargs={"pk": self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
