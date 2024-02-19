from faker import Faker

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models.cart import Cart, CartItem


class CartFactory:
    faker = Faker()

    @staticmethod
    def create_cart():
        cart = Cart.objects.create()
        return str(cart.id)

    @classmethod
    def add_one_item(cls):
        cart_id = cls.create_cart()
        product = ProductFactory.create_product(has_images=True)
        variant = product.variants.first()
        CartItem.objects.create(cart_id=cart_id, variant_id=variant.id, quantity=1)
        return str(cart_id)

    @classmethod
    def add_multiple_items(cls):
        cart_id = cls.create_cart()
        product = ProductFactory.create_product(has_images=True, is_variable=True)
        variants_list = list(product.variants.all())

        for variant in variants_list:
            CartItem.objects.create(cart_id=cart_id, variant_id=variant.id, quantity=1)

        return str(cart_id)
