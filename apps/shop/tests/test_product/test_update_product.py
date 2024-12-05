import json

from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import (
    ProductFactory,
    ProductFactoryHelper,
)
from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class UpdateProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # TODO add sku field
        cls.new_payload = {
            "name": "updated name",
            "slug": "new-slug",
            "description": "updated description",
            "status": Product.STATUS_ARCHIVED,
            "price": 1001,
            "stock": 4002,
            "options": [],
        }
        cls.options = ProductFactoryHelper().unique_options()
        cls.new_payload_with_options = cls.new_payload.copy()
        cls.new_payload_with_options["options"] = cls.options

    def setUp(self):
        self.set_admin_user_authorization()

        # create sample product for test update
        (
            self.simple_product_payload,
            self.simple_product,
        ) = ProductFactory.create_product(get_payload=True)
        (
            self.variable_product_payload,
            self.variable_product,
        ) = ProductFactory.create_product(is_variable=True, get_payload=True)

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_update_product_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------
    # --- Test Update Product ---
    # ---------------------------

    def test_update_product(self):
        """
        If a product variant already exists, its price, stock, and SKU will not be changed.
        To update these fields, you must update the variant through the variants' endpoint.

        If a product variant is new, the provided price, stock, and SKU will be used to create the new variant.
        """
        # request
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            self.new_payload,
        )

        # expected product
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], self.new_payload.get("name"))
        self.assertEqual(expected["description"], self.new_payload.get("description"))
        self.assertEqual(expected["status"], self.new_payload.get("status"))
        self.assertEqual(expected["slug"], self.new_payload.get("slug"))

        # expected product date and time
        self.assertExpectedDatetimeFormat(expected)

        # expected product options
        self.assertIsNone(expected["options"])

        # expected product variants
        self.assertEqual(len(expected["variants"]), 1)
        self.assertExpectedVariants(
            expected["variants"],
            expected_price=self.simple_product_payload.get("price"),
            expected_stock=self.simple_product_payload.get("stock"),
        )

        # expected product media
        self.assertIsNone(expected["images"])

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    def test_update_with_empty_payload(self):
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_required_fields(self):
        # request
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            data={"name": self.new_payload.get("name")},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(expected["name"], self.new_payload.get("name"))

    def test_update_product_without_required_fields(self):
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            data={"description": self.new_payload.get("description")},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_product(self):
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": 999}), self.new_payload
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_valid_status(self):
        payloads = [
            {"name": "Test", "status": Product.STATUS_ACTIVE},
            {"name": "Test", "status": Product.STATUS_ARCHIVED},
            {"name": "Test", "status": Product.STATUS_DRAFT},
            {"name": "Test", "status": ""},
            {"name": "Test", "status": " "},
            {"name": "Test", "status": "1"},
            {"name": "Test", "status": "blob"},
            {"name": "Test", "status": 1},
        ]
        for payload in payloads:
            response = self.put_json(
                reverse("product-detail", kwargs={"pk": self.simple_product.id}),
                payload,
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            match payload["status"]:
                case Product.STATUS_ACTIVE:
                    self.assertEqual(response.data["status"], Product.STATUS_ACTIVE)
                case Product.STATUS_ARCHIVED:
                    self.assertEqual(response.data["status"], Product.STATUS_ARCHIVED)
                case Product.STATUS_DRAFT:
                    self.assertEqual(response.data["status"], Product.STATUS_DRAFT)
                case _:
                    self.assertEqual(response.data["status"], Product.STATUS_DRAFT)

    def test_update_invalid_status(self):
        payloads = [
            {"name": "Test", "status": None},
            {"name": "Test", "status": False},
            {"name": "Test", "status": True},
            {"name": "Test", "status": []},
        ]

        for payload in payloads:
            response = self.put_json(
                reverse("product-detail", kwargs={"pk": self.simple_product.id}),
                payload,
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_invalid_price(self):
        invalid_options = [
            {"name": "test", "price": -10},
            {"name": "test", "price": None},
            {"name": "test", "price": ""},
        ]
        for payload in invalid_options:
            response = self.put_json(
                reverse("product-detail", kwargs={"pk": self.simple_product.id}),
                payload,
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_invalid_stock(self):
        invalid_options = [
            {"name": "test", "stock": -10},
            {"name": "test", "stock": None},
            {"name": "test", "stock": ""},
            {"name": "test", "stock": 1.2},
        ]
        for payload in invalid_options:
            response = self.put_json(
                reverse("product-detail", kwargs={"pk": self.simple_product.id}),
                payload,
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_field_updated_at(self):
        ...
        # product_data = {
        #     "name": "test product",
        #     "status": Product.STATUS_ACTIVE,
        #     "price": 11,
        #     "stock": 11,
        #     "sku": 11,
        #     "options": [],
        # }
        # product = ProductService.create_product(**product_data)
        # self.assertIsNotNone(product.published_at)
        #
        # product_data["status"] = Product.STATUS_DRAFT
        # product = ProductService.create_product(**product_data)
        # self.assertIsNone(product.published_at)
        #
        # product_data["status"] = Product.STATUS_ARCHIVED
        # product = ProductService.create_product(**product_data)
        # self.assertIsNone(product.published_at)


class UpdateProductOptionsTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.new_payload = {
            "name": "updated name",
            "slug": "new-slug",
            "description": "updated description",
            "status": Product.STATUS_ARCHIVED,
            "price": 1001,
            "stock": 4002,
            "options": [],
        }

        cls.option = ProductFactoryHelper().unique_options(1)
        cls.new_payload_with_one_option = cls.new_payload.copy()
        cls.new_payload_with_one_option["options"] = (
            {"option_name": "material", "items": ["Cotton", "Nylon"]},
        )

        cls.options = ProductFactoryHelper().unique_options()
        cls.new_payload_with_multi_options = cls.new_payload.copy()
        cls.new_payload_with_multi_options["options"] = cls.options

    def setUp(self):
        self.set_admin_user_authorization()

        # create sample product for test update
        (
            self.simple_product_payload,
            self.simple_product,
        ) = ProductFactory.create_product(get_payload=True)
        (
            self.variable_product_payload,
            self.variable_product,
        ) = ProductFactory.create_product(
            is_variable=True, get_payload=True, count_of_options=2
        )

    # ---------------------------
    # --- Test Add New Option ---
    # ---------------------------

    def test_update_simple_product_add_new_options(self):
        # request
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            self.new_payload_with_multi_options,
        )

        # expected product
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(
            expected["name"], self.new_payload_with_multi_options.get("name")
        )
        self.assertEqual(
            expected["description"],
            self.new_payload_with_multi_options.get("description"),
        )
        self.assertEqual(
            expected["status"], self.new_payload_with_multi_options.get("status")
        )
        self.assertEqual(
            expected["slug"], self.new_payload_with_multi_options.get("slug")
        )

        # expected product date and time
        self.assertExpectedDatetimeFormat(expected)

        # expected product options
        self.assertIsNotNone(expected["options"])
        self.assertEqual(len(expected["options"]), 3)
        self.assertExpectedOptions(
            expected["options"], self.new_payload_with_multi_options.get("options")
        )

        # expected product variants
        self.assertTrue(len(expected["variants"]) == 8)
        self.assertExpectedVariants(
            expected["variants"],
            self.new_payload_with_multi_options.get("price"),
            self.new_payload_with_multi_options.get("stock"),
        )

        # expected product media
        self.assertIsNone(expected["images"])

    def test_update_variable_product_add_new_option(self):
        # request
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.variable_product.id}),
            self.new_payload_with_multi_options,
        )

        # expected product
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], self.new_payload_with_one_option.get("name"))
        self.assertEqual(
            expected["description"], self.new_payload_with_one_option.get("description")
        )
        self.assertEqual(
            expected["status"], self.new_payload_with_one_option.get("status")
        )
        self.assertEqual(expected["slug"], self.new_payload_with_one_option.get("slug"))

        # expected product date and time
        self.assertExpectedDatetimeFormat(expected)

        # expected product options
        self.assertIsNotNone(expected["options"])
        self.assertEqual(len(expected["options"]), 3)

        # expected product variants
        self.assertTrue(len(expected["variants"]) == 8)
        self.assertExpectedVariants(
            expected["variants"],
            self.new_payload_with_one_option.get("price"),
            self.new_payload_with_one_option.get("stock"),
        )

        # expected product media
        self.assertIsNone(expected["images"])

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    def test_update_with_required_options(self):
        # request
        payload = {
            "name": "Test Product",
            "options": [{"option_name": "color", "items": ["red"]}],
        }
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}), payload
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()

        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(
            expected["description"], self.simple_product_payload.get("description")
        )
        self.assertEqual(expected["status"], Product.STATUS_DRAFT)

        # expected product date and time
        self.assertExpectedDatetimeFormat(expected)

        # expected product options
        self.assertEqual(len(expected["options"]), 1)
        self.assertExpectedOptions(expected["options"], payload["options"])

        # expected product variants
        # self.assertTrue(len(expected["variants"]) == 1)
        # self.assertExpectedVariants(expected["variants"])

    def test_update_with_duplicate_options(self):
        options = [
            {"option_name": "color", "items": ["red", "green"]},
            {"option_name": "size", "items": ["S", "M"]},
            {"option_name": "material", "items": ["Cotton", "Nylon"]},
        ]
        final_options = [
            {"option_name": "color", "items": ["red", "green", "black"]},
            {"option_name": "size", "items": ["S", "M"]},
            {"option_name": "material", "items": ["Cotton", "Nylon"]},
        ]

        # request
        payload = {
            "name": "test",
            "options": options + [{"option_name": "color", "items": ["black"]}],
        }
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}), payload
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected["options"]), 3)
        self.assertExpectedDatetimeFormat(expected)

        self.assertExpectedOptions(expected["options"], final_options)
        # self.assertExpectedVariants(expected["variants"])

    def test_update_with_duplicate_items_in_options(self):
        # request
        payload = {
            "name": "blob",
            "options": [
                {"option_name": "color", "items": ["red", "blue", "red"]},
                {"option_name": "size", "items": ["S", "L"]},
            ],
        }
        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}), payload
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()

        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(
            expected["description"], self.simple_product_payload.get("description")
        )
        self.assertEqual(expected["status"], Product.STATUS_DRAFT)

        # expected product date and time
        self.assertExpectedDatetimeFormat(expected)

        # expected product options
        self.assertEqual(len(expected["options"]), 2)
        self.assertExpectedOptions(expected["options"], payload["options"])

        # expected product variants
        # self.assertTrue(len(expected["variants"]) == 4)
        # self.assertExpectedVariants(expected["variants"])

    def test_update_with_invalid_options(self):
        invalid_options = [
            {"name": "test", "options": ""},
            {"name": "test", "options": [""]},
            {"name": "test", "options": ["blob"]},
            {"name": "test", "options": [{}]},
            {"name": "test", "options": [{"option_name": []}]},
            {"name": "test", "options": [{"option_name": ""}]},
            {"name": "test", "options": [{"option_name": "", "items": []}]},
            {"name": "test", "options": [{"option_name": "", "items": ["a"]}]},
            {"name": "test", "options": [{"option_name": "blob", "items": ""}]},
            # {
            #     "name": "test",
            #     "options": [{"option_name": "blob", "items": [1]}],
            # },
            {
                "name": "test",
                "options": [{"option_name": "blob", "items_blob": ["a"]}],
            },
            {
                "name": "test",
                "options": [{"option_blob": "blob", "items": ["a"]}],
            },
            {
                "name": "test",
                "options": [{"items": ["a"], "option_blob": "blob"}],
            },
            {
                "name": "test",
                "options": [{"option_name": "blob", "items": [["a", "b"]]}],
            },
        ]
        for payload in invalid_options:
            response = self.put_json(
                reverse("product-detail", kwargs={"pk": self.simple_product.id}),
                payload,
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_variable_product_with_max_3_options(self):
        payload = {
            "name": "blob",
            "options": [
                {"option_name": "color", "items": ["red"]},
                {"option_name": "size", "items": ["small"]},
                {"option_name": "material", "items": ["x1", "x2"]},
                {"option_name": "blob", "items": ["b"]},
            ],
        }

        response = self.put_json(
            reverse("product-detail", kwargs={"pk": self.variable_product.id}), payload
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# TODO test update when delete an option
# TODO test update with invalid slug
# TODO test update with existing options (for variable product)
# TODO test `updated_at` is set correctly
class PartialUpdateProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create product
        # (
        #     cls.simple_product_payload,
        #     cls.simple_product,
        # ) = ProductFactory.create_product(get_payload=True)
        # (
        #     cls.variable_product_payload,
        #     cls.variable_product,
        # ) = ProductFactory.create_product(is_variable=True, get_payload=True)

    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def _test_update_product_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_update_product_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _test_partial_update_product_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_partial_update_product_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------
    # --- Test Update Product ---
    # ---------------------------

    def _test_update_product_required_fields(self):
        # make request
        payload = {"name": "updated name"}
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(expected["name"], "updated name")

    def _test_update_product_without_required_fields(self):
        payload = {"description": "updated description"}
        response = self.client.put(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _test_partial_update_product(self):
        payloads = [
            {"name": "partial updated name"},
            {"description": "partial updated description"},
            {"status": Product.STATUS_ARCHIVED},
        ]
        for payload in payloads:
            response = self.client.patch(
                reverse("product-detail", kwargs={"pk": self.simple_product.id}),
                json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            expected = response.json()
            for key, value in payload.items():
                self.assertEqual(expected[key], value)

    def _test_partial_update_product_without_required_fields(self):
        # make request
        payload = {"description": "updated description"}
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.simple_product.id}),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(expected["description"], "updated description")

    def _test_update_product_published_after_update_status_to_active(self):
        # create with status draft
        product = ProductFactory.create_product(status=Product.STATUS_DRAFT)

        # update status to active
        payload = {"status": Product.STATUS_ACTIVE}
        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": product.id}),
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertDatetimeFormat(expected["published_at"])


# todo test_max_3_options
# todo test with repetitive items

# todo move the `product-option` update to the `product` update.
