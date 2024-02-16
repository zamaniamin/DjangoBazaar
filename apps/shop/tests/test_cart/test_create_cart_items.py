import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models.cart import Cart


class CreateCartItemsTest(CoreBaseTestCase):
    simple_product = None
    variable_product = None

    @classmethod
    def setUpTestData(cls):
        # simple product
        cls.simple_product = ProductFactory.create_product(has_images=True)
        cls.simple_product_variant = cls.simple_product.variants.first()

        # variable product
        cls.variable_product = ProductFactory.create_product(
            is_variable=True, has_images=True
        )
        cls.variable_product_variants = cls.variable_product.variants.first()
        cls.variable_product_variants_list = list(cls.variable_product.variants.all())

        # cart
        cart = Cart.objects.create()
        cls.cart_id = cart.id

    def test_create_one_cart_item(self):
        # request
        payload = {"variant": self.simple_product_variant.id, "quantity": 1}
        response = self.client.post(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id}),
            json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)

        # expected variant
        variant = expected["variant"]
        price = float(self.simple_product_variant.price)
        self.assertIsInstance(variant, dict)
        self.assertEqual(len(variant), 7)
        self.assertEqual(variant["id"], self.simple_product_variant.id)
        self.assertEqual(variant["product_id"], self.simple_product.id)
        self.assertEqual(variant["price"], price)
        self.assertEqual(variant["stock"], self.simple_product_variant.stock)
        self.assertEqual(variant["option1"], self.simple_product_variant.option1)
        self.assertEqual(variant["option2"], self.simple_product_variant.option2)
        self.assertEqual(variant["option3"], self.simple_product_variant.option3)

        # expected image
        self.assertIsInstance(expected["image"], str)

        # expected quantity and item_total
        self.assertEqual(expected["quantity"], 1)
        self.assertAlmostEqual(expected["item_total"], round(price, 2), places=2)

    def test_create_one_cart_item_with_two_quantity(self):
        # request
        quantity = 2
        payload = {"variant": self.variable_product_variants.id, "quantity": quantity}
        response = self.client.post(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id}),
            json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)

        # expected variant
        price = float(self.variable_product_variants.price)
        variant = expected["variant"]
        self.assertIsInstance(variant, dict)
        self.assertEqual(len(variant), 7)
        self.assertEqual(variant["id"], self.variable_product_variants.id)

        self.assertEqual(variant["product_id"], self.variable_product.id)
        self.assertEqual(variant["price"], price)
        self.assertEqual(variant["stock"], self.variable_product_variants.stock)
        self.assertEqual(
            variant["option1"], str(self.variable_product_variants.option1)
        )
        self.assertEqual(
            variant["option2"], str(self.variable_product_variants.option2)
        )
        self.assertEqual(
            variant["option3"], str(self.variable_product_variants.option3)
        )

        # expected image
        self.assertIsInstance(expected["image"], str)

        # expected quantity and item_total
        self.assertEqual(expected["quantity"], quantity)
        item_total = price * quantity
        self.assertAlmostEqual(expected["item_total"], round(item_total, 2), places=2)

    def test_cart_total_price(self):
        # request
        total_price: float = 0
        for variant in self.variable_product_variants_list:
            payload = {"variant": variant.id, "quantity": 1}
            response = self.client.post(
                reverse("cart-items-list", kwargs={"cart_pk": self.cart_id}),
                json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            expected = response.json()
            total_price += expected["item_total"]

        # expected
        response = self.client.get(reverse("cart-detail", kwargs={"pk": self.cart_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertAlmostEqual(expected["total_price"], round(total_price, 2), places=2)


# TODO test remove cart item
# TODO test update cart item quantity
# TODO test item total price
# TODO test access permissions
# TODO fix error 500 on create cart items ['“7” is not a valid UUID.']
# TODO fix error 500 on create cart items if uuid dos not exist [FOREIGN KEY constraint failed], should return 404
# TODO rename guest users in test to Anonymous user
# TODO add cart to faker
# print(response.data)
