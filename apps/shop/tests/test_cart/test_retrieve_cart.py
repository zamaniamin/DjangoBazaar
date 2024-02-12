from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models.cart import Cart


class ListCartTest(CoreBaseTestCase):
    simple_product = None
    variable_product = None
    variable_product_variants = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # simple product
        cls.simple_product = ProductFactory.create_product(has_images=True)
        cls.simple_product_variant = cls.simple_product.variants.first()

        # variable product
        cls.variable_product = ProductFactory.create_product(
            has_images=True, is_variable=True
        )
        cls.variable_product_variants = list(cls.variable_product.variants.all())

        # cart
        cart = Cart.objects.create()
        cls.cart_id = cart.id
        # for variant in cls.variable_product_variants:
        #     CartItem.objects.create(
        #         cart_id=cart.id,
        #         variant=variant.variant,
        #         quantity=1
        #     )

    def test_list_carts_by_admin(self):
        self.set_admin_user_authorization()
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

    # def test_retrieve


# TODO test retrieve cart
# TODO test retrieve cart item
