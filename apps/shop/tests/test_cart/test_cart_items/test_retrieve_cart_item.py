from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class ListCartItemsTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cart_id, cls.cart_items = CartFactory.add_multiple_items(get_items=True)

    def api_path(self) -> str:
        return reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response_body), len(self.cart_items))
        for item in self.response_body:
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

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_list(self):
        response = self.send_request()
        self.validate_response_body(response)

    def test_list_empty_items(self):
        cart_id = CartFactory.create_cart()
        response = self.send_request(
            reverse("cart-items-list", kwargs={"cart_pk": cart_id})
        )
        self.assertHTTPStatusCode(response)

    def test_list_with_invalid_cart_id(self):
        response = self.send_request(reverse("cart-items-list", kwargs={"cart_pk": 11}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RetrieveCartItemTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cart_id, cls.cart_item = CartFactory.add_one_item(get_item=True)

    def api_path(self) -> str:
        return reverse(
            "cart-items-detail",
            kwargs={"cart_pk": self.cart_id, "pk": self.cart_item.id},
        )

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        expected_cart_item = self.response_body
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

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        response = self.send_request(
            reverse(
                "cart-items-detail",
                kwargs={"cart_pk": cart_id, "pk": cart_item.id},
            )
        )
        self.validate_response_body(response)

    def test_retrieve_with_invalid_cart_id(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        response = self.client.get(
            reverse("cart-items-detail", kwargs={"cart_pk": 11, "pk": cart_item.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
