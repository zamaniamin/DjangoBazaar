from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIDeleteTestCaseMixin
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class DestroyCartItemsTest(APIDeleteTestCaseMixin):

    def setUp(self):
        super().setUp()
        self.cart_id, self.cart_item = CartFactory.add_one_item(get_item=True)

    def api_path(self) -> str:
        return reverse(
            "cart-items-detail",
            kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user(status.HTTP_204_NO_CONTENT)

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user(status.HTTP_204_NO_CONTENT)

    def test_delete(self):
        response = self.send_request()
        self.assertHTTPStatusCode(response)

        # test cart item is removed
        response = self.client.get(self.api_path())
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_delete_with_invalid_cart_pk(self):
        response = self.send_request(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": 7, "pk": self.cart_item.id},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)
