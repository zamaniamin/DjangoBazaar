from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import APITestCaseMixin
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class DestroyCartItemsTestMixin(APITestCaseMixin):
    def setUp(self):
        self.cart_id, self.cart_item = CartFactory.add_one_item(get_item=True)

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    def test_delete_item_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.delete(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.delete(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # -----------------------------
    # --- Test Delete Cart Item ---
    # -----------------------------

    def test_delete_item(self):
        response = self.client.delete(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- test cart item is removed ---
        response = self.client.get(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_with_invalid_cart_pk(self):
        response = self.client.delete(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": 7, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
