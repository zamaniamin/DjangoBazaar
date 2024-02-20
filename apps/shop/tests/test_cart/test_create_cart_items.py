import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.cart.cart_factory import CartFactory
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product


class CreateCartItemsTest(CoreBaseTestCase):
    simple_product = None
    variable_product = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

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
        cls.cart_id = CartFactory.create_cart()

    def setUp(self):
        self.payload = {"variant": self.simple_product_variant.id, "quantity": 1}

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_cart_item_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.post(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id}),
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_cart_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id}),
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_cart_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id}),
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ------------------------------
    # --- Test Create Cart Items ---
    # ------------------------------

    def test_create_one_cart_item(self):
        # request
        response = self.client.post(
            reverse("cart-items-list", kwargs={"cart_pk": self.cart_id}),
            json.dumps(self.payload),
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

    # -----------------------
    # --- Invalid cart_pk ---
    # -----------------------

    def test_create_cart_item_with_invalid_cart_pk(self):
        response = self.client.post(
            reverse("cart-items-list", kwargs={"cart_pk": 7}),
            json.dumps(self.payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_cart_item_if_uuid_not_exist(self):
        response = self.client.post(
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": "5a092b03-7920-4c61-ba98-f749296e4750"},
            ),
            json.dumps(self.payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --------------------------------------------
    # --- Test if product status is not active ---
    # --------------------------------------------

    def test_create_cart_item_with_draft_product(self):
        product = ProductFactory.create_product(status=Product.STATUS_DRAFT)
        product_variant = product.variants.first()
        response = self.client.post(
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
            json.dumps({"variant": product_variant.id, "quantity": 1}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_cart_item_with_archived_product(self):
        product = ProductFactory.create_product(status=Product.STATUS_ARCHIVED)
        product_variant = product.variants.first()
        response = self.client.post(
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
            json.dumps({"variant": product_variant.id, "quantity": 1}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------
    # --- Test if variant stock is out of stock ---
    # ---------------------------------------------

    def test_create_cart_item_if_variant_not_in_stock(self):
        product = ProductFactory.create_product(stock=0)
        product_variant = product.variants.first()
        response = self.client.post(
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
            json.dumps({"variant": product_variant.id, "quantity": 1}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_cart_item_quantity_bigger_than_stock(self):
        product = ProductFactory.create_product(stock=3)
        product_variant = product.variants.first()
        response = self.client.post(
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
            json.dumps({"variant": product_variant.id, "quantity": 4}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -----------------------
    # --- Invalid Payload ---
    # -----------------------

    def test_create_cart_item_if_variant_not_exist(self):
        response = self.client.post(
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
            json.dumps({"variant": 9999, "quantity": 1}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_cart_item_without_image(self):
        product = ProductFactory.create_product()
        product_variant = product.variants.first()
        response = self.client.post(
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
            json.dumps({"variant": product_variant.id, "quantity": 1}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    # TODO test if variant id is invalid type
    # TODO test if quantity is invalid type

# TODO test increase item quantity If it is already in the card
# TODO fix error 500 on create cart items ['“7” is not a valid UUID.']
# TODO fix error 500 on create cart items if uuid dos not exist [FOREIGN KEY constraint failed], should return 404
