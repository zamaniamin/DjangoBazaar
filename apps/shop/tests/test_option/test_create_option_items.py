import json

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import Product


class CreateOptionItemsTest(CoreBaseTestCase):
    variable_product = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        self.option = OptionFactory.create_option()
        self.payload = {"item_name": "red"}

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_option_item_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_pk": str(self.option.id)}),
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_option_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_name": self.option_name}),
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_option_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_name": self.option_name}),
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ------------------------------
    # --- Test Create option Items ---
    # ------------------------------

    def test_create_one_option_item(self):
        # request
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_name": self.option_name}),
            json.dumps(self.payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected["item_name"], str)

        # expected quantity and item_total
        self.assertEqual(expected["quantity"], 1)

    def test_create_one_option_item_if_already_exist(self):
        option_name, option_item = OptionFactory.add_one_item(get_item=True)
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_name": option_name}),
            json.dumps({"option_name": option_item.option_name, "quantity": 1}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_option_total_price(self):
        # request
        total_price: float = 0
        payload = {"option_name": self.option_name, "quantity": 1}
        response = self.client.post(
            reverse("option-items-list", kwargs={"option_name": self.option_name}),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        total_price += expected["item_total"]

        # expected
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option_name})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertAlmostEqual(expected["total_price"], round(total_price, 2), places=2)

    # --------------------------------------------
    # --- Test if product status is not active ---
    # --------------------------------------------

    def test_create_option_item_with_draft_product(self):
        product = ProductFactory.create_product(status=Product.STATUS_DRAFT)
        product_variant = product.variants.first()
        response = self.client.post(
            reverse(
                "option-items-list",
                kwargs={"option_name": self.option_name},
            ),
            json.dumps({"variant": product_variant.id, "quantity": 1}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_option_item_with_archived_product(self):
        product = ProductFactory.create_product(status=Product.STATUS_ARCHIVED)
        response = self.client.post(
            reverse(
                "option-items-list",
                kwargs={"option_name": self.option_name},
            ),
            json.dumps({"quantity": 1}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------
    # --- Test if variant stock is out of stock ---
    # ---------------------------------------------

    def test_create_option_item_if_variant_not_in_stock(self):
        product = ProductFactory.create_product(stock=0)
        response = self.client.post(
            reverse(
                "option-items-list",
                kwargs={"option_name": self.option_name},
            ),
            json.dumps({"quantity": 1}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_option_item_quantity_bigger_than_stock(self):
        product = ProductFactory.create_product(stock=3)
        response = self.client.post(
            reverse(
                "option-items-list",
                kwargs={"option_name": self.option_name},
            ),
            json.dumps({"quantity": 4}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -----------------------
    # --- Invalid Payload ---
    # -----------------------

    def test_create_option_item_without_image(self):
        product = ProductFactory.create_product()
        response = self.client.post(
            reverse(
                "option-items-list",
                kwargs={"option_name": self.option_name},
            ),
            json.dumps({"quantity": 1}),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_option_item_invalid_quantity(self):
        invalid_payloads = [
            {"quantity": -1},
            {"quantity": 0},
            {"quantity": "0"},
            {"quantity": None},
            {"quantity": True},
            {"quantity": []},
            {"quantity": ""},
            {"variant": 1},
            {},
        ]
        for invalid_payload in invalid_payloads:
            response = self.client.post(
                reverse(
                    "option-items-list",
                    kwargs={"option_name": self.option_name},
                ),
                json.dumps(invalid_payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
