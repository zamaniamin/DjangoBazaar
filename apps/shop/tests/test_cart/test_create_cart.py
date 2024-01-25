import json
import uuid

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import BaseCoreTestCase
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models.cart import Cart


class CreateCartTest(BaseCoreTestCase):
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
    simple_product = None
    variable_product = None

    @classmethod
    def setUpTestData(cls):
        # --- simple product ---
        cls.simple_product = ProductFactory.create_product(has_images=True)
        cls.simple_product_variant = cls.simple_product.variants.first()

        # --- variable product ---
        cls.variable_product = ProductFactory.create_product(
            is_variable=True, has_images=True
        )
        cls.variable_product_variants = list(cls.variable_product.variants.all())

        # --- cart ---
        cart = Cart.objects.create()
        cls.cart_id = cart.id

    def test_create_one_cart_item(self):
        # --- request ---
        payload = {"variant": self.simple_product_variant.id, "quantity": 1}
        response = self.client.post(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id}),
            json.dumps(payload),
            content_type="application/json",
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # TODO test items data
        # TODO test item_total value
        # TODO test total_price value
        # print(response.data)

    def test_create_cart_items(self):
        # --- request ---
        for variant in self.variable_product_variants:
            payload = {"variant": variant.id, "quantity": 1}
            response = self.client.post(
                reverse("cart-items-list", kwargs={"cart_pk": self.cart_id}),
                json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # --- expected ---
        # response = self.client.get(reverse("cart-list"))
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len())
        # print(response.json())


class RetrieveCartTest(BaseCoreTestCase):
    simple_product = None
    variable_product = None
    variable_product_variants = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # --- simple product ---
        cls.simple_product = ProductFactory.create_product(has_images=True)
        cls.simple_product_variant = cls.simple_product.variants.first()

        # --- variable product ---
        cls.variable_product = ProductFactory.create_product(
            has_images=True, is_variable=True
        )
        cls.variable_product_variants = list(cls.variable_product.variants.all())

        # --- cart ---
        cart = Cart.objects.create()
        cls.cart_id = cart.id
        # for variant in cls.variable_product_variants:
        #     CartItem.objects.create(
        #         cart_id=cart.id,
        #         variant=variant.variant,
        #         quantity=1
        #     )

    def test_list_carts(self):
        response = self.client.get(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_carts_by_admin(self):
        self.set_admin_authorization()
        response = self.client.get(reverse("cart-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_retrieve


# TODO test retrieve cart
# TODO test retrieve cart item
# TODO test remove cart
# TODO test remove cart item
# TODO test update cart item quantity
# TODO test cart total price
# TODO test item total price
# TODO test access permissions
# TODO fix error 500 on create cart items ['“7” is not a valid UUID.']
# TODO fix error 500 on create cart items if uuid dos not exist [FOREIGN KEY constraint failed], should return 404
# TODO rename guest users in test to Anonymous user
# TODO add cart to faker
# print(response.data)
