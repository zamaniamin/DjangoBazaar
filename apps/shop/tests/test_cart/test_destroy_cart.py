from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class DestroyCartTest(CoreBaseTestCase):
    def setUp(self):
        self.cart_id, self.cart_item = CartFactory.add_one_item(get_item=True)

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    def test_delete_cart_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.delete(
            path=reverse(viewname="cart-detail", kwargs={"pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_cart_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            path=reverse(viewname="cart-detail", kwargs={"pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_cart_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.delete(
            path=reverse(viewname="cart-detail", kwargs={"pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_cart(self):
        # make request
        response = self.client.delete(
            path=reverse(viewname="cart-detail", kwargs={"pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # test cart is removed
        response = self.client.get(
            path=reverse(viewname="cart-detail", kwargs={"pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # test cart items are removed
        response = self.client.get(
            path=reverse(
                viewname="cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_cart_with_invalid_pk(self):
        response = self.client.delete(
            path=reverse(viewname="cart-detail", kwargs={"pk": 7})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_cart_with_multi_items(self):
        # create a cart with multi items
        self.cart_id, self.cart_items = CartFactory.add_multiple_items(get_items=True)

        # make request
        response = self.client.delete(
            path=reverse(viewname="cart-detail", kwargs={"pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # test cart is removed
        response = self.client.get(
            path=reverse(viewname="cart-detail", kwargs={"pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # test cart items are removed
        for item in self.cart_items:
            response = self.client.get(
                path=reverse(
                    viewname="cart-items-detail",
                    kwargs={"cart_pk": self.cart_id, "pk": item.id},
                )
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
