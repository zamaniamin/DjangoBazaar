from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory


class DestroyOptionTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()
        self.option = OptionFactory.create_option()
        self.option_item = OptionFactory.add_one_option_item(self.option.id)

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    def test_delete_option_by_admin(self):
        response = self.client.delete(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_option_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_option_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.delete(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_option(self):
        # --- request for delete an option ---
        response = self.client.delete(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- assert option is removed ---
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # --- assert option items are removed ---
        response = self.client.get(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_option_404(self):
        response = self.client.delete(reverse("option-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
