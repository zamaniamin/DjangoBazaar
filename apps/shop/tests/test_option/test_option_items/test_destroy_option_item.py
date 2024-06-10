from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory


class DestroyOptionTest(CoreBaseTestCase):
    def setUp(self):
        self.option = OptionFactory.create_option()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    def test_delete_option_by_admin(self):
        self.set_admin_user_authorization()
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
        response = self.client.delete(
            reverse("option-detail", kwargs={"pk": self.option_id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- test option is removed ---
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option_id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # --- test option items are removed ---
        response = self.client.get(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_option_404(self):
        response = self.client.delete(reverse("option-detail", kwargs={"pk": 7}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _test_delete_option_with_multi_items(self):
        self.option_id, self.option_items = OptionFactory.add_multiple_items(
            get_items=True
        )
        response = self.client.delete(
            reverse("option-detail", kwargs={"pk": self.option_id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- test option is removed ---
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option_id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # --- test option items are removed ---
        for item in self.option_items:
            response = self.client.get(
                reverse(
                    "option-items-detail",
                    kwargs={"option_pk": self.option_id, "pk": item.id},
                )
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DestroyOptionItemsTest(CoreBaseTestCase):
    def setUp(self):
        self.option_id, self.option_item = OptionFactory.add_one_item(get_item=True)

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    def test_delete_option_item_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.delete(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_option_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_option_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.delete(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_option_item(self):
        response = self.client.delete(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- test option item is removed ---
        response = self.client.get(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_option_item_with_invalid_option_pk(self):
        response = self.client.delete(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": 7, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
