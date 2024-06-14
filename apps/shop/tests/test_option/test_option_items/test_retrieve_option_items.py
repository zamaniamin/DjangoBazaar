from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory


class ListOptionItemsTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()
        self.option = OptionFactory.create_option()
        self.option_items = OptionFactory.add_option_item_list(self.option.id)

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_list_option_items_by_admin(self):
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_option_items_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_option_items_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------
    # --- Test List Option Items ---
    # ------------------------------

    def test_list_option_items(self):
        # make request
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #
        expected_option_items = response.json()
        self.assertEqual(len(expected_option_items), len(self.option_items))

        for item in expected_option_items:
            self.assertEqual(
                set(item.keys()),
                {
                    "id",
                    "item_name",
                },
            )

    def test_option_items_empty_list(self):
        # request
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "item_name",
            },
        )
        self.assertIsInstance(expected["results"], list)
        self.assertEqual(len(expected["results"]), 0)

    def test_list_option_items_with_invalid_option_id(self):
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": 7})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_options_without_items(self):
        # --- test list one option ---
        OptionFactory.create_option()
        response = self.client.get(reverse("option-list"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 1)
        self.assertIn("items", expected[0])

        # --- test list two options ---
        OptionFactory.create_option()
        response = self.client.get(reverse("option-list"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 2)
        for option in expected:
            self.assertIn("items", option)

    def test_list_options_with_items(self):
        # TODO get option list
        # TODO get option items list
        response = self.client.get(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = response.json()
        self.assertEqual(len(expected), 1)
        for option in expected:
            self.assertIsInstance(uuid.UUID(option["id"]), uuid.UUID)
            self.assertIsInstance(option["items"], list)
            for item in option["items"]:
                self.assertIn("id", item)


class RetrieveOptionItemTest(CoreBaseTestCase):
    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    def setUp(self):
        self.set_admin_user_authorization()

    @classmethod
    def setUpTestData(cls):
        cls.option = OptionFactory.create_option()
        cls.option_items = OptionFactory.add_option_item_list(cls.option.id)
        super().setUpTestData()
        cls.option_id, cls.option_item = OptionFactory.add_one_option_item(
            cls.option.id
        )

    def test_retrieve_option_item_by_admin(self):
        response = self.client.get(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_option_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_option_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_option_item(self):
        option_item = OptionFactory.add_one_option_item(self.option.id)
        response = self.client.get(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_option_item = response.json()
        self.assertIn("id", expected_option_item)

    def test_retrieve_option_with_invalid_option_id(self):
        option_item = OptionFactory.add_one_option_item(self.option.id)
        response = self.client.get(
            reverse(
                "option-items-detail", kwargs={"option_pk": 11, "pk": option_item.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _test_retrieve_option_with_one_item(self):
        # TODO move this method to test retrieve option item
        option_id = OptionFactory.add_one_option_item(self.option.id)
        response = self.client.get(reverse("option-detail", kwargs={"pk": option_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 3)
        self.assertIsInstance(uuid.UUID(expected["id"]), uuid.UUID)
        self.assertIsInstance(expected["items"], list)
        item = expected["items"][0]
        self.assertIn("id", item)

    def test_retrieve_option_with_multi_items(self):
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = response.json()
        self.assertEqual(len(expected), 3)
        self.assertIsInstance(uuid.UUID(expected["id"]), uuid.UUID)
        self.assertIsInstance(expected["items"], list)
        for item in expected["items"]:
            self.assertIn("id", item)
        self.assertIn("total_price", expected)
