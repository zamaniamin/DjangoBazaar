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

    def setUp(self):
        self.cart_id = CartFactory.create_cart()
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

    def test_create_one_cart_item_if_already_exist(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        response = self.client.post(
            reverse("cart-items-list", kwargs={"cart_pk": cart_id}),
            json.dumps({"variant": cart_item.variant_id, "quantity": 1}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_create_cart_item_invalid_variant_id(self):
        invalid_payloads = [
            {"variant": -1, "quantity": 1},
            {"variant": 0, "quantity": 1},
            {"variant": "0", "quantity": 1},
            {"variant": "11", "quantity": 1},
            {"variant": None, "quantity": 1},
            {"variant": True, "quantity": 1},
            {"variant": [], "quantity": 1},
            {"variant": "", "quantity": 1},
            {"quantity": 1},
            {},
        ]
        for invalid_payload in invalid_payloads:
            response = self.client.post(
                reverse(
                    "cart-items-list",
                    kwargs={"cart_pk": self.cart_id},
                ),
                json.dumps(invalid_payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_cart_item_invalid_quantity(self):
        invalid_payloads = [
            {"quantity": -1, "variant": 1},
            {"quantity": 0, "variant": 1},
            {"quantity": "0", "variant": 1},
            {"quantity": None, "variant": 1},
            {"quantity": True, "variant": 1},
            {"quantity": [], "variant": 1},
            {"quantity": "", "variant": 1},
            {"variant": 1},
            {},
        ]
        for invalid_payload in invalid_payloads:
            response = self.client.post(
                reverse(
                    "cart-items-list",
                    kwargs={"cart_pk": self.cart_id},
                ),
                json.dumps(invalid_payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
