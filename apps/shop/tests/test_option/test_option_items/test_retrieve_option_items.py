from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory


class ListOptionItemsTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()
        cls.option_items = OptionFactory.add_option_item_list(cls.option.id)

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_list_items_by_admin(self):
        response = self.client.get(
            path=reverse(
                viewname="option-items-list", kwargs={"option_pk": self.option.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_items_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            path=reverse(
                viewname="option-items-list", kwargs={"option_pk": self.option.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_items_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            path=reverse(
                viewname="option-items-list", kwargs={"option_pk": self.option.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -----------------------
    # --- Test List Items ---
    # -----------------------

    def test_list_items(self):
        # make request
        response = self.client.get(
            path=reverse(
                viewname="option-items-list", kwargs={"option_pk": self.option.id}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
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

    def test_list_items_with_invalid_option_pk(self):
        response = self.client.get(
            path=reverse(viewname="option-items-list", kwargs={"option_pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_if_option_dont_have_item(self):
        # create an option without items
        option = OptionFactory.create_option("material")

        # request
        response = self.client.get(
            path=reverse(viewname="option-items-list", kwargs={"option_pk": option.id})
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 0)


class RetrieveOptionItemTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()
        cls.option_item = OptionFactory.add_one_option_item(cls.option.id)

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_retrieve_item_by_admin(self):
        response = self.client.get(
            path=reverse(
                viewname="option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            path=reverse(
                viewname="option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            path=reverse(
                viewname="option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_item(self):
        response = self.client.get(
            path=reverse(
                viewname="option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_items_if_option_not_exist(self):
        response = self.client.get(
            path=reverse(
                viewname="option-items-detail",
                kwargs={"option_pk": 999, "pk": self.option_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_item_if_item_not_exist(self):
        response = self.client.get(
            path=reverse(
                viewname="option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": 999},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
