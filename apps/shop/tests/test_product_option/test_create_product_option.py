from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class CreateProductOptionTest(ProductBaseTestCase):
    # variable_product = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.payload = {"option_name": "test option", "items": ["item 1", "item 2"]}
        cls.repetitive_payload = {"option_name": "color", "items": ["item 1", "item 2"]}
        cls.variable_product = ProductFactory.create_product(is_variable=True)

    def setUp(self):
        self.set_admin_user_authorization()
        self.simple_product = ProductFactory.create_product()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_product_option_by_admin(self):
        # request
        response = self.post_json(
            reverse(
                "product-options-list", kwargs={"product_pk": self.simple_product.id}
            ),
            self.payload,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_option_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.post_json(
            reverse("option-items-list", kwargs={"option_pk": self.simple_product.id}),
            self.payload,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_option_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.post_json(
            reverse("option-items-list", kwargs={"option_pk": self.simple_product.id}),
            self.payload,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------------
    # --- Test Create Product Option ---
    # ----------------------------------

    def test_create_product_option(self):
        # request
        response = self.post_json(
            reverse(
                "product-options-list", kwargs={"product_pk": self.simple_product.id}
            ),
            self.payload,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # expected
        expected: list = response.json()
        option = expected[0]
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), 1)
        self.assertIsInstance(option["id"], int)
        self.assertGreater(option["id"], 0)
        self.assertEqual(option["option_name"], self.payload["option_name"])
        self.assertCountEqual(option["items"], self.payload["items"])

        # test this new option is assigned to the product
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.simple_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected product options
        expected_product = response.json()
        self.assertEqual(len(expected_product["options"]), 1)
        self.assertExpectedOptions(expected_product["options"], [self.payload])

    def test_create_product_option_with_repetitive_option_name(self):
        # before create
        # todo check color items

        # request
        response = self.post_json(
            reverse(
                "product-options-list",
                kwargs={"product_pk": self.variable_product.id},
            ),
            self.repetitive_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # expected
        options = response.json()
        self.assertIsInstance(options, list)
        self.assertEqual(len(options), 3)

        for option in options:
            self.assertEqual(
                set(option.keys()),
                {
                    "id",
                    "option_name",
                    "items",
                },
            )

        color_option: dict = next(
            (
                option
                for option in options
                if option["option_name"] == self.repetitive_payload["option_name"]
            ),
            None,
        )
        self.assertIsInstance(color_option["id"], int)
        self.assertGreater(color_option["id"], 0)
        self.assertEqual(
            color_option["option_name"], self.repetitive_payload["option_name"]
        )
        self.assertCountEqual(color_option["items"], self.repetitive_payload["items"])

        # test this new option is assigned to the product
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.variable_product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected product options
        expected_product = response.json()
        self.assertEqual(len(expected_product["options"]), 3)
        self.assertExpectedOptions(expected_product["options"], options)


# todo test_max_3_options
# todo test with repetitive items
