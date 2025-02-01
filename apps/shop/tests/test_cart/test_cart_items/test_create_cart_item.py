from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIPostTestCaseMixin
from apps.shop.demo.factory.cart.cart_factory import CartFactory
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product


class CreateCartItemsTest(APIPostTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # simple product
        cls.simple_product = ProductFactory.customize(has_image=True)
        cls.simple_product_variant = cls.simple_product.variants.first()

        # variable product
        cls.variable_product = ProductFactory.customize(
            is_variable=True, has_image=True
        )
        cls.variable_product_variants = cls.variable_product.variants.first()
        cls.variable_product_variants_list = list(cls.variable_product.variants.all())
        cls.payload = {"variant": cls.simple_product_variant.id, "quantity": 1}

    def setUp(self):
        super().setUp()
        self.cart_id = CartFactory.create_cart()

    def api_path(self) -> str:
        return reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertIsInstance(self.response_body["id"], int)

        # expected variant
        variant = self.response_body["variant"]
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
        self.assertIsInstance(self.response_body["image"], str)

        # expected quantity and item_total
        self.assertEqual(self.response_body["quantity"], 1)
        self.assertAlmostEqual(
            self.response_body["item_total"], round(price, 2), places=2
        )

    def test_access_permission_by_regular_user(self):
        response = self.check_access_permission_by_regular_user(
            status.HTTP_201_CREATED, self.payload
        )
        self.validate_response_body(response, self.payload)

    def test_access_permission_by_anonymous_user(self):
        response = self.check_access_permission_by_anonymous_user(
            status.HTTP_201_CREATED, self.payload
        )
        self.validate_response_body(response, self.payload)

    def test_create(self):
        response = self.send_request(self.payload)
        self.validate_response_body(response, self.payload)

    def test_create_if_item_already_exist(self):
        cart_id, cart_item = CartFactory.add_one_item(get_item=True)
        payload = {"variant": cart_item.variant_id, "quantity": 1}
        response = self.send_request(
            payload, reverse("cart-items-list", kwargs={"cart_pk": cart_id})
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_cart_total_price(self):
        total_price: float = 0
        for variant in self.variable_product_variants_list:
            payload = {"variant": variant.id, "quantity": 1}
            response = self.send_request(
                payload, reverse("cart-items-list", kwargs={"cart_pk": self.cart_id})
            )
            self.assertHTTPStatusCode(response)
            expected = response.json()
            total_price += expected["item_total"]

        # expected
        response = self.client.get(reverse("cart-detail", kwargs={"pk": self.cart_id}))
        self.assertHTTPStatusCode(response, status.HTTP_200_OK)
        expected = response.json()
        self.assertAlmostEqual(expected["total_price"], round(total_price, 2), places=2)

    def test_create_with_invalid_cart_pk(self):
        response = self.send_request(
            self.payload, reverse("cart-items-list", kwargs={"cart_pk": 7})
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_if_uuid_not_exist(self):
        response = self.send_request(
            self.payload,
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": "5a092b03-7920-4c61-ba98-f749296e4750"},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_create_with_draft_product(self):
        product = ProductFactory.customize(status=Product.STATUS_DRAFT)
        product_variant = product.variants.first()
        payload = {"variant": product_variant.id, "quantity": 1}
        response = self.send_request(
            payload,
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_with_archived_product(self):
        product = ProductFactory.customize(status=Product.STATUS_ARCHIVED)
        product_variant = product.variants.first()
        payload = {"variant": product_variant.id, "quantity": 1}
        response = self.send_request(
            payload,
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_if_variant_not_in_stock(self):
        product = ProductFactory.customize(stock=0)
        product_variant = product.variants.first()
        payload = {"variant": product_variant.id, "quantity": 1}
        response = self.send_request(
            payload,
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_quantity_bigger_than_stock(self):
        product = ProductFactory.customize(stock=3)
        product_variant = product.variants.first()
        payload = {"variant": product_variant.id, "quantity": 4}
        response = self.send_request(
            payload,
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_if_variant_not_exist(self):
        payload = {"variant": 9999, "quantity": 1}
        response = self.send_request(
            payload,
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
        )
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_without_image(self):
        product = ProductFactory.customize()
        product_variant = product.variants.first()
        payload = {"variant": product_variant.id, "quantity": 1}
        response = self.send_request(
            payload,
            reverse(
                "cart-items-list",
                kwargs={"cart_pk": self.cart_id},
            ),
        )
        self.assertHTTPStatusCode(response)

    def test_create_invalid_variant_id(self):
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
            response = self.send_request(
                invalid_payload,
                reverse(
                    "cart-items-list",
                    kwargs={"cart_pk": self.cart_id},
                ),
            )
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_create_item_invalid_quantity(self):
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
            response = self.send_request(
                invalid_payload,
                reverse(
                    "cart-items-list",
                    kwargs={"cart_pk": self.cart_id},
                ),
            )
            self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)
