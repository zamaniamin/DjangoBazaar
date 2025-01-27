from apps.core.tests.mixin import APITestCaseMixin


class ProductBaseTestCaseMixin(APITestCaseMixin):
    def assertExpectedOptions(self, expected_options, payload_options: list):
        """
        Asserts the expected options in the response.
        """

        self.assertIsInstance(expected_options, list)

        for option in expected_options:
            self.assertIsInstance(option["id"], int)
            self.assertIsInstance(option["option_name"], str)

            # Assert that the 'option_name' exists in the 'option' list
            self.assertTrue(
                any(
                    payload_option["option_name"] == option["option_name"]
                    for payload_option in expected_options
                )
            )

            # Expected items
            self.assertIsInstance(option["items"], list)
            self.assertExpectedItems(option, payload_options)

    def assertExpectedItems(self, expected_option, payload_options):
        """
        Asserts the expected items in the response.
        """

        option_name = expected_option["option_name"]
        option_items = expected_option["items"]
        self.assertIsInstance(option_items, list)

        # Iterate through each item in the actual option's 'items'
        for item in option_items:
            # Find the corresponding payload option in the payload_options list
            payload_option = next(
                (
                    payload_option
                    for payload_option in payload_options
                    if payload_option["option_name"] == option_name
                ),
                None,
            )

            # Check if the payload option corresponding to the current item exists
            self.assertIsNotNone(
                payload_option,
                f"Option '{expected_option['option_name']}' not found in payload options",
            )

            # Assert that the item name in the response matches the payload items for the corresponding option
            self.assertIn(
                item,
                payload_option["items"],
                f"Item name '{item}' not found in payload items",
            )

    def assertExpectedVariants(
        self,
        expected_variants: list,
        expected_price: int | float = None,
        expected_stock: int = None,
    ):
        """
        Asserts the expected variants in the response.
        """
        # TODO add sku

        self.assertIsInstance(expected_variants, list)

        for variant in expected_variants:
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
