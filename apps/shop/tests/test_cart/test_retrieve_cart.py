import uuid

from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.cart.cart_factory import CartFactory


class ListCartTest(APIGetTestCaseMixin):
    def api_path(self) -> str:
        return reverse("cart-list")

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)

    def test_access_permission_by_regular_user(self):
        self.authorization_as_regular_user()
        response = self.send_request()
        self.assertHTTPStatusCode(response, status.HTTP_403_FORBIDDEN)

    def test_list_carts_by_anonymous_user(self):
        self.authorization_as_anonymous_user()
        response = self.send_request()
        self.assertHTTPStatusCode(response, status.HTTP_401_UNAUTHORIZED)

    def test_list(self):
        response = self.send_request()
        self.assertHTTPStatusCode(response)

    def test_empty_list(self):
        response = self.send_request()
        self.assertHTTPStatusCode(response)
        self.assertEqual(len(response.json()), 0)

    def test_list_without_items(self):
        CartFactory.create_cart()
        response = self.send_request()
        self.assertHTTPStatusCode(response)
        expected = response.json()
        self.assertEqual(len(expected), 1)
        self.assertIn("items", expected[0])
        self.assertIn("total_price", expected[0])

        # test list two carts
        CartFactory.create_cart()
        response = self.send_request(reverse("cart-list"))
        self.assertHTTPStatusCode(response)
        expected = response.json()
        self.assertEqual(len(expected), 2)
        for cart in expected:
            self.assertIn("items", cart)
            self.assertIn("total_price", cart)

    def test_list_with_items(self):
        CartFactory.add_multiple_items()
        response = self.send_request(reverse("cart-list"))
        self.assertHTTPStatusCode(response)
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


class RetrieveCartTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.cart_id = CartFactory.add_multiple_items()

    def api_path(self) -> str:
        return reverse("cart-detail", kwargs={"pk": self.cart_id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response_body), 3)
        self.assertIsInstance(uuid.UUID(self.response_body["id"]), uuid.UUID)
        self.assertIsInstance(self.response_body["items"], list)
        for item in self.response_body["items"]:
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
        self.assertIn("total_price", self.response_body)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve_with_one_item(self):
        cart_id = CartFactory.add_one_item()
        response = self.send_request(reverse("cart-detail", kwargs={"pk": cart_id}))
        self.validate_response_body(response)

    def test_retrieve_with_multi_items(self):
        cart_id = CartFactory.add_multiple_items()
        response = self.send_request(reverse("cart-detail", kwargs={"pk": cart_id}))
        self.validate_response_body(response)

    def test_retrieve_with_invalid_pk(self):
        response = self.send_request(reverse("cart-detail", kwargs={"pk": "11"}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.send_request(reverse("cart-detail", kwargs={"pk": 11}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
