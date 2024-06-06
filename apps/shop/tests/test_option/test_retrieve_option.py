import uuid

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory


class ListOptionTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_list_options_by_admin(self):
        response = self.client.get(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_options_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_options_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -----------------------
    # --- Test List options ---
    # -----------------------

    def test_empty_list(self):
        response = self.client.get(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_list_options_without_items(self):
        # --- test list one option ---
        OptionFactory.create_option()
        response = self.client.get(reverse("option-list"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 1)
        self.assertIn("items", expected[0])
        self.assertIn("total_price", expected[0])

        # --- test list two options ---
        OptionFactory.create_option()
        response = self.client.get(reverse("option-list"))

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 2)
        for option in expected:
            self.assertIn("items", option)
            self.assertIn("total_price", option)

    def test_list_options_with_items(self):
        OptionFactory.add_multiple_items()
        response = self.client.get(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 1)
        for option in expected:
            self.assertIsInstance(uuid.UUID(option["id"]), uuid.UUID)
            self.assertIsInstance(option["items"], list)
            for item in option["items"]:
                self.assertIn("id", item)
            self.assertIn("total_price", option)


class RetrieveOptionTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option_id = OptionFactory.add_multiple_items()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_option_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(reverse("option-detail", kwargs={"pk": self.option_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_option_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(reverse("option-detail", kwargs={"pk": self.option_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_option_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(reverse("option-detail", kwargs={"pk": self.option_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----------------------------
    # --- Test Retrieve a option ---
    # ----------------------------

    def test_retrieve_option_with_one_item(self):
        option_id = OptionFactory.add_one_item()
        response = self.client.get(reverse("option-detail", kwargs={"pk": option_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 3)
        self.assertIsInstance(uuid.UUID(expected["id"]), uuid.UUID)
        self.assertIsInstance(expected["items"], list)
        item = expected["items"][0]
        self.assertIn("id", item)
      
    def test_retrieve_option_with_multi_items(self):
        option_id = OptionFactory.add_multiple_items()
        response = self.client.get(reverse("option-detail", kwargs={"pk": option_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 3)
        self.assertIsInstance(uuid.UUID(expected["id"]), uuid.UUID)
        self.assertIsInstance(expected["items"], list)
        for item in expected["items"]:
            self.assertIn("id", item)
        self.assertIn("total_price", expected)

    def test_retrieve_option_with_invalid_pk(self):
        response = self.client.get(reverse("option-detail", kwargs={"pk": "11"}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(reverse("option-detail", kwargs={"pk": 11}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ListOptionItemsTest(CoreBaseTestCase):
    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def setUp(self):
        self.option_id, self.option_items = OptionFactory.add_multiple_items(get_items=True)

    def test_list_option_items_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": self.option_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_option_items_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": self.option_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_option_items_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": self.option_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_option_items(self):
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": self.option_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_option_items = response.json()
        self.assertEqual(len(expected_option_items), len(self.option_items))

        for item in expected_option_items:
            self.assertIn("id", item)

    def test_list_empty_option_items(self):
        option_id = OptionFactory.create_option()
        response = self.client.get(
            reverse("option-items-list", kwargs={"option_pk": option_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_option_items_with_invalid_option_id(self):
        response = self.client.get(reverse("option-items-list", kwargs={"option_pk": 11}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RetrieveOptionItemTest(CoreBaseTestCase):
    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option_id, cls.option_item = OptionFactory.add_one_item(get_item=True)

    def test_retrieve_option_item_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option_id, "pk": self.option_item.id},
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
        option_id, option_item = OptionFactory.add_one_item(get_item=True)
        response = self.client.get(
            reverse(
                "option-items-detail", kwargs={"option_pk": option_id, "pk": option_item.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_option_item = response.json()
        self.assertIn("id", expected_option_item)

    def test_retrieve_option_with_invalid_option_id(self):
        option_id, option_item = OptionFactory.add_one_item(get_item=True)
        response = self.client.get(
            reverse("option-items-detail", kwargs={"option_pk": 11, "pk": option_item.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
