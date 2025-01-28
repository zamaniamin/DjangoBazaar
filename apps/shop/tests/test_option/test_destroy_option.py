from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APITestCaseMixin
from apps.shop.demo.factory.option.option_factory import OptionFactory


class DestroyOptionTest(APITestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()
        cls.option_item = OptionFactory.add_one_option_item(cls.option.id)

    def setUp(self):
        self.set_admin_user_authorization()

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

    # --------------------------
    # --- Test Delete Option ---
    # --------------------------

    def test_delete_option(self):
        # request for delete an option
        response = self.client.delete(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # assert option is removed
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # assert option items are removed
        response = self.client.get(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_if_option_not_exist(self):
        response = self.client.delete(reverse("option-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
