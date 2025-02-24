from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIDeleteTestCaseMixin
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class DestroyCartTest(APIDeleteTestCaseMixin):
    def api_path(self) -> str:
        return reverse("carts:cart-detail", kwargs={"pk": self.cart_id})

    def setUp(self):
        self.cart_id, self.cart_item = CartFactory.add_one_item(get_item=True)

    def test_access_permission_by_regular_user(self):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.assertHTTPStatusCode(response, status.HTTP_204_NO_CONTENT)

    def test_access_permission_by_anonymous_user(self):
        self.authorization_as_anonymous_user()
        response = self.send_request()
        self.assertHTTPStatusCode(response, status.HTTP_204_NO_CONTENT)

    def test_delete(self):
        response = self.send_request()
        self.assertHTTPStatusCode(response)

        # test cart is removed
        response = self.client.get(self.api_path())
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

        # test cart items are removed
        response = self.client.get(
            reverse(
                "carts:item",
                kwargs={"cart_id": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_delete_with_invalid_pk(self):
        response = self.client.delete(reverse("carts:cart-detail", kwargs={"pk": 7}))
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_delete_with_multi_items(self):
        self.cart_id, self.cart_items = CartFactory.add_multiple_items(get_items=True)
        response = self.send_request()
        self.assertHTTPStatusCode(response)

        # test cart is removed
        response = self.client.get(self.api_path())
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

        # test cart items are removed
        for item in self.cart_items:
            response = self.client.get(
                reverse(
                    "carts:item",
                    kwargs={"cart_id": self.cart_id, "pk": item.id},
                )
            )
            self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
