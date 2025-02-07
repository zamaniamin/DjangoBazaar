from django.utils.text import slugify

from apps.core.tests.mixin import APIAssertMixin
from apps.shop.demo.factory.attribute.attribute_factory import ATTRIBUTE_COUNT
from apps.shop.models.product import Product


class ProductAssertMixin(APIAssertMixin):
    def assertExpectedProductResponse(
        self,
        response_body: dict,
        payload: dict = None,
        options_len: int = None,
        variants_len: int = 1,
        attributes_len: int = None,
        images_len: int = None,
    ):
        self.assertExpectedKeys(response_body)
        self.assertIsInstance(response_body["id"], int)
        self.assertEqual(response_body["name"], payload["name"])
        self.asserExpectedSlug(response_body, payload)
        self.assertEqual(
            response_body["description"],
            payload.get("description"),
        )
        self.asserExpectedStatus(response_body, payload)
        self.assertExpectedOptions(response_body, payload, options_len)
        self.assertExpectedVariants(
            response_body,
            expected_price=payload.get("price"),
            expected_stock=payload.get("stock"),
            variants_len=variants_len,
        )
        self.assertEqual(response_body["category"], payload.get("category"))
        self.assertExpectedAttributes(response_body, payload, attributes_len)
        self.assertExpectedPrice(response_body)
        self.assertExpectedImages(response_body, payload, images_len)
        self.assertExpectedProductDatetimeFormat(response_body)
        # TODO add media assertion

    def assertExpectedKeys(self, response_body: dict):
        self.assertEqual(len(response_body), 15)
        self.assertEqual(
            set(response_body.keys()),
            {
                "id",
                "name",
                "slug",
                "description",
                "status",
                "options",
                "variants",
                "category",
                "attributes",
                "price",
                "total_stock",
                "images",
                "created_at",
                "updated_at",
                "published_at",
            },
        )

    def asserExpectedSlug(self, response_body: dict, payload):
        self.assertEqual(
            response_body.get("slug"),
            payload.get("slug", slugify(payload.get("name"), allow_unicode=True)),
        )

    def asserExpectedStatus(self, response_body: dict, payload):
        self.assertEqual(
            response_body.get("status"), payload.get("status", Product.STATUS_DRAFT)
        )

    def assertExpectedOptions(
        self, response_body: dict, payload: dict = None, options_len: int = None
    ):
        """
        Asserts the expected options in the response.
        """
        options = response_body.get("options")
        if options:
            self.assertIsInstance(options, list)
            self.assertEqual(len(options), options_len)

            for option in options:
                self.assertIsInstance(option["id"], int)
                self.assertIsInstance(option["option_name"], str)

                # Assert that the 'option_name' exists in the 'option' list
                self.assertTrue(
                    any(
                        payload_option["option_name"] == option["option_name"]
                        for payload_option in options
                    )
                )

                # Expected items in option
                self.assertIsInstance(option["items"], list)
                self.assertExpectedItemsInOption(option, payload.get("options"))
        else:
            self.assertIsNone(options)

    def assertExpectedItemsInOption(self, option: dict, options_payload):
        option_name = option["option_name"]
        option_items = option["items"]
        self.assertIsInstance(option_items, list)
        self.assertIsInstance(options_payload, list)

        # Iterate through each item in the actual option's 'items'
        for item in option_items:
            # Find the corresponding payload option in the payload_options list
            payload_option = next(
                (
                    payload_option
                    for payload_option in options_payload
                    if payload_option["option_name"] == option_name
                ),
                None,
            )

            # Check if the payload option corresponding to the current item exists
            self.assertIsNotNone(
                payload_option,
                f"Option '{option['option_name']}' not found in payload options",
            )

            # Assert that the item name in the response matches the payload items for the corresponding option
            self.assertIn(
                item,
                payload_option["items"],
                f"Item name '{item}' not found in payload items",
            )

    def assertExpectedVariants(
        self,
        response_body: dict,
        expected_price: int | float = None,
        expected_stock: int = None,
        variants_len: int = 1,
    ):
        """
        Asserts the expected variants in the response.
        """
        # TODO add sku
        variants = response_body.get("variants")
        self.assertIsInstance(variants, list)
        self.assertEqual(len(variants), variants_len)
        for variant in variants:
            self.assertEqual(len(variant), 11)
            self.assertIsInstance(variant["id"], int)
            self.assertIsInstance(variant["product_id"], int)

            # price
            self.assertIsInstance(variant["price"], float)
            if expected_price is not None:
                self.assertEqual(variant["price"], expected_price)

            # stock
            self.assertIsInstance(variant["stock"], int)
            if expected_stock is not None:
                self.assertEqual(variant["stock"], expected_stock)

            # options
            # TODO check the value base on items len
            self.assertIsInstance(variant["option1"], str | None)
            self.assertIsInstance(variant["option2"], str | None)
            self.assertIsInstance(variant["option3"], str | None)

            # datetime
            self.assertDatetimeFormat(variant["created_at"])
            self.assertDatetimeFormat(variant["updated_at"])

    def assertExpectedAttributes(
        self, response_body: dict, payload: dict = None, attributes_len: int = None
    ):
        attributes = response_body.get("attributes")
        if attributes:
            self.assertEqual(
                len(attributes),
                ATTRIBUTE_COUNT if attributes_len is None else attributes_len,
            )
            for attribute in attributes:
                self.assertEqual(
                    set(attribute.keys()),
                    {
                        "attribute_id",
                        "attribute_name",
                        "items",
                    },
                )
                for item in attribute["items"]:
                    self.assertEqual(
                        set(item.keys()),
                        {
                            "item_id",
                            "item_name",
                        },
                    )

    def assertExpectedPrice(self, response_body: dict):
        price = response_body.get("price")
        self.assertEqual(
            set(price.keys()),
            {"min_price", "max_price"},
        )

    def assertExpectedImages(
        self, response_body: dict, payload: dict = None, images_len: int = None
    ):
        self.assertIsNone(response_body["images"])

    def assertExpectedProductDatetimeFormat(self, expected_product):
        """
        Asserts the expected format for datetime strings.
        """
        self.assertDatetimeFormat(expected_product.get("created_at"))
        self.assertDatetimeFormat(expected_product.get("updated_at"))
        if expected_product.get("published_at"):
            self.assertDatetimeFormat(expected_product.get("published_at"))
        else:
            self.assertIs(expected_product.get("published_at"), None)
