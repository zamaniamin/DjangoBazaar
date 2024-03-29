import uuid

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class ListCartTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_list_carts_by_admin(self):
        response = self.client.get(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_carts_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_carts_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -----------------------
    # --- Test List Carts ---
    # -----------------------

    def test_empty_list(self):
        response = self.client.get(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_list_carts_without_items(self):
        # --- test list one cart ---
        CartFactory.create_cart()
        response = self.client.get(reverse("cart-list"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 1)
        self.assertIn("items", expected[0])
        self.assertIn("total_price", expected[0])

        # --- test list two carts ---
        CartFactory.create_cart()
        response = self.client.get(reverse("cart-list"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 2)
        for cart in expected:
            self.assertIn("items", cart)
            self.assertIn("total_price", cart)

    def test_list_carts_with_items(self):
        CartFactory.add_multiple_items()
        response = self.client.get(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 1)
        for cart in expected:
            self.assertIsInstance(uuid.UUID(cart["id"]), uuid.UUID)
            self.assertIsInstance(cart["items"], list)
            for item in cart["items"]:
                self.assertIn("id", item)
                self.assertIn("variant", item)
                self.assertIn("id", item["variant"])
                self.assertIn("product_id", item["variant"])
                self.assertIn("price", item["variant"])
                self.assertIn("stock", item["variant"])
                self.assertIn("option1", item["variant"])
                self.assertIn("option2", item["variant"])
                self.assertIn("option3", item["variant"])
                self.assertIn("image", item)
                self.assertIn("quantity", item)
                self.assertIn("item_total", item)
            self.assertIn("total_price", cart)


class RetrieveCartTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cart_id = CartFactory.add_multiple_items()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_cart_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(reverse("cart-detail", kwargs={"pk": self.cart_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_cart_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(reverse("cart-detail", kwargs={"pk": self.cart_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_cart_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(reverse("cart-detail", kwargs={"pk": self.cart_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----------------------------
    # --- Test Retrieve a Cart ---
    # ----------------------------

    def test_retrieve_cart_with_one_item(self):
        cart_id = CartFactory.add_one_item()
        response = self.client.get(reverse("cart-detail", kwargs={"pk": cart_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 3)
        self.assertIsInstance(uuid.UUID(expected["id"]), uuid.UUID)
        self.assertIsInstance(expected["items"], list)
        item = expected["items"][0]
        self.assertIn("id", item)
        self.assertIn("variant", item)
        self.assertIn("id", item["variant"])
        self.assertIn("product_id", item["variant"])
        self.assertIn("price", item["variant"])
        self.assertIn("stock", item["variant"])
        self.assertIn("option1", item["variant"])
        self.assertIn("option2", item["variant"])
        self.assertIn("option3", item["variant"])
        self.assertIn("image", item)
        self.assertIn("quantity", item)
        self.assertIn("item_total", item)
        self.assertIn("total_price", expected)

    def test_retrieve_cart_with_multi_items(self):
        cart_id = CartFactory.add_multiple_items()
        response = self.client.get(reverse("cart-detail", kwargs={"pk": cart_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 3)
        self.assertIsInstance(uuid.UUID(expected["id"]), uuid.UUID)
        self.assertIsInstance(expected["items"], list)
        for item in expected["items"]:
            self.assertIn("id", item)
            self.assertIn("variant", item)
            self.assertIn("id", item["variant"])
            self.assertIn("product_id", item["variant"])
            self.assertIn("price", item["variant"])
            self.assertIn("stock", item["variant"])
            self.assertIn("option1", item["variant"])
            self.assertIn("option2", item["variant"])
            self.assertIn("option3", item["variant"])
            self.assertIn("image", item)
            self.assertIn("quantity", item)
            self.assertIn("item_total", item)
        self.assertIn("total_price", expected)

    def test_retrieve_cart_with_invalid_pk(self):
        response = self.client.get(reverse("cart-detail", kwargs={"pk": "11"}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(reverse("cart-detail", kwargs={"pk": 11}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ListCartItemsTest(CoreBaseTestCase):
    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def setUp(self):
        self.cart_id, self.cart_items = CartFactory.add_multiple_items(get_items=True)

    def test_list_cart_items_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cart_items_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cart_items_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cart_items(self):
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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

    def test_list_empty_cart_items(self):
        cart_id = CartFactory.create_cart()
        response = self.client.get(
            reverse("cart-items-list", kwargs={"cart_pk": cart_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_cart_items_with_invalid_cart_id(self):
        response = self.client.get(reverse("cart-items-list", kwargs={"cart_pk": 11}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RetrieveCartItemTest(CoreBaseTestCase):
    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cart_id, cls.cart_item = CartFactory.add_one_item(get_item=True)

    def test_retrieve_cart_item_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_cart_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_cart_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_cart_item(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        response = self.client.get(
            reverse(
                "cart-items-detail", kwargs={"cart_pk": cart_id, "pk": cart_item.id}
            )
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
        self.assertIn("item_total", expected_cart_item)

    def test_retrieve_cart_with_invalid_cart_id(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        response = self.client.get(
            reverse("cart-items-detail", kwargs={"cart_pk": 11, "pk": cart_item.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
