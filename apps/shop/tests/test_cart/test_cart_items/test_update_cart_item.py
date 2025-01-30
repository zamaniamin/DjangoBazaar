from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIUpdateTestCaseMixin
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class UpdateCartItemTest(APIUpdateTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cart_id, cls.cart_item = CartFactory.add_one_item(get_item=True)

    def api_path(self) -> str:
        return reverse(
            "cart-items-detail",
            kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
        )

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertIn("id", self.response_body)
        self.assertIn("variant", self.response_body)
        variant = self.response_body["variant"]
        self.assertIn("id", variant)
        self.assertIn("product_id", variant)
        self.assertIn("price", variant)
        self.assertIn("stock", variant)
        self.assertIn("option1", variant)
        self.assertIn("option1", variant)
        self.assertIn("option3", variant)
        self.assertIn("image", self.response_body)
        self.assertIn("quantity", self.response_body)

    def test_access_permission_by_regular_user(self):
        payload = {"quantity": 3}
        response = self.check_access_permission_by_regular_user(
            status.HTTP_200_OK, payload, True
        )
        self.validate_response_body(response, payload)

    def test_access_permission_by_anonymous_user(self):
        payload = {"quantity": 3}
        response = self.check_access_permission_by_anonymous_user(
            status.HTTP_200_OK, payload, True
        )
        self.validate_response_body(response, payload)

    def test_update(self):
        payload = {"quantity": 3}
        response = self.send_patch_request(payload)
        self.validate_response_body(response, payload)

    def test_update_quantity(self):
        new_quantity = self.cart_item.quantity + 1
        price = float(self.cart_item.variant.price)
        item_total = price * new_quantity
        payload = {"quantity": new_quantity}
        response = self.send_patch_request(payload)
        self.validate_response_body(response, payload)
        self.assertAlmostEqual(
            self.response_body["item_total"], round(item_total, 2), places=2
        )

    def test_update_quantity_bigger_than_stock(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True, stock=1)
        payload = {"quantity": 3}
        response = self.send_patch_request(
            payload,
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": cart_id, "pk": cart_item.id},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_update_if_variant_is_out_of_stock(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True, stock=0)
        payload = {"quantity": 3}
        response = self.send_patch_request(
            payload,
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": cart_id, "pk": cart_item.id},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_update_if_cart_not_exist(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        payload = {"quantity": 3}
        response = self.send_patch_request(
            payload,
            reverse(
                "cart-items-detail",
                kwargs={
                    "cart_pk": "5a092b03-7920-4c61-ba98-f749296e4750",
                    "pk": cart_item.id,
                },
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_update_if_item_not_exist(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        payload = {"quantity": 3}
        response = self.send_patch_request(
            payload,
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": cart_id, "pk": 1111},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_update_with_invalid_cart_pk(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        payload = {"quantity": 3}
        response = self.send_patch_request(
            payload,
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": 7, "pk": cart_item.id},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)


# TODO test update with invalid payload
