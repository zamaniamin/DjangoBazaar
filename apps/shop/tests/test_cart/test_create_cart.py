import uuid

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import BaseCoreTestCase
from apps.shop.faker.product_faker import SimpleProductFaker, VariableProductFaker


class CreateCartTest(BaseCoreTestCase):
    @classmethod
    def setUpTestData(cls):
        # create some products
        cls.simple_product = (
            SimpleProductFaker.populate_active_simple_product_with_image()
        )
        cls.variable_product = (
            VariableProductFaker.populate_active_variable_product_with_image()
        )

    def test_create_cart(self):
        response = self.client.post(
            reverse("cart-list"), {}, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertEqual(len(expected), 3)
        self.assertIsInstance(uuid.UUID(expected["id"]), uuid.UUID)
        self.assertIsInstance(expected["items"], list)
        self.assertEqual(len(expected["items"]), 0)
        self.assertEqual(expected["total_price"], 0)


class CreateCartItemsTest(BaseCoreTestCase):
    ...


# TODO test create new cart item
# TODO test remove cart
# TODO test remove cart item
# TODO test update cart item quantity
# TODO test cart total price
# TODO test item total price
# print(response.data)
