from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class ListCartItemsTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(self):
        super().setUpTestData()
        self.cart_id, self.cart_items = CartFactory.add_multiple_items(get_items=True)

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_list_items_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_items_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_items_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -----------------------
    # --- Test List Items ---
    # -----------------------

    def test_list_items(self):
        # make request
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected_cart_items = response.json()
        self.assertEqual(len(expected_cart_items), len(self.cart_items))

        for item in expected_cart_items:
            self.assertIn("id", item)
            self.assertIn("variant", item)
            variant = item["variant"]
            self.assertIn("id", variant)
            self.assertIn("product_id", variant)
            self.assertIn("price", variant)
            self.assertIn("stock", variant)
            self.assertIn("option1", variant)
            self.assertIn("option1", variant)
            self.assertIn("option3", variant)
            self.assertIn("image", item)
            self.assertIn("quantity", item)
            self.assertIn("item_total", item)

    def test_list_empty_items(self):
        cart_id = CartFactory.create_cart()

        # make request
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_items_with_invalid_cart_id(self):
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": 11})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RetrieveCartItemTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cart_id, cls.cart_item = CartFactory.add_one_item(get_item=True)

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_retrieve_item_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --------------------------
    # --- Test Retrieve Item ---
    # --------------------------

    def test_retrieve_item(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)

        # make request
        response = self.client.get(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": cart_id, "pk": cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
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
        self.assertIn("item_total", expected_cart_item)

    def test_retrieve_item_with_invalid_cart_id(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)

        # make request
        response = self.client.get(
            reverse(
                "cart-items-detail", kwargs={"cart_pk": 11, "pk": cart_item.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
