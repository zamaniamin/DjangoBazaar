import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class UpdateCartItemTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cart_id, cls.cart_item = CartFactory.add_one_item(get_item=True)

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_update_item_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.patch(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.patch(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.patch(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item_quantity(self):
        new_quantity = self.cart_item.quantity + 1
        price = float(self.cart_item.variant.price)
        item_total = price * new_quantity
        response = self.client.patch(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            ),
            json.dumps({"quantity": new_quantity}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_cart_item = response.json()
        self.assertIn("id", expected_cart_item)
        self.assertIn("variant", expected_cart_item)
        variant = expected_cart_item["variant"]
        self.assertIn("id", variant)
        self.assertIn("product_id", variant)
        self.assertIn("price", variant)
        self.assertIn("stock", variant)
        self.assertIn("option1", variant)
        self.assertIn("option1", variant)
        self.assertIn("option3", variant)
        self.assertIn("image", expected_cart_item)
        self.assertIn("quantity", expected_cart_item)
        self.assertAlmostEqual(
            expected_cart_item["item_total"], round(item_total, 2), places=2
        )

    def test_update_item_quantity_bigger_than_stock(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True, stock=1)

        response = self.client.patch(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": cart_id, "pk": cart_item.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_if_variant_not_in_stock(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True, stock=0)

        response = self.client.patch(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": cart_id, "pk": cart_item.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_if_cart_not_exist(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        response = self.client.patch(
            reverse(
                "cart-items-detail",
                kwargs={
                    "cart_pk": "5a092b03-7920-4c61-ba98-f749296e4750",
                    "pk": cart_item.id,
                },
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_if_not_exist(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        response = self.client.patch(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": cart_id, "pk": 1111},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_with_invalid_cart_pk(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        response = self.client.patch(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": 7, "pk": cart_item.id},
            ),
            json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# TODO test update with invalid payload
