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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_options_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --------------------------
    # --- Test List Options ----
    # --------------------------

    def test_option_list(self):
        # create a list of options
        OptionFactory.create_option_list()

        # request
        response = self.client.get(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )

        option_list = expected["results"]
        self.assertIsInstance(option_list, list)
        self.assertEqual(len(option_list), 2)

        for option in option_list:
            self.assertEqual(
                set(option.keys()),
                {
                    "id",
                    "option_name",
                    "updated_at",
                    "created_at",
                },
            )

    def test_option_empty_list(self):
        # request
        response = self.client.get(reverse("option-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )
        self.assertIsInstance(expected["results"], list)
        self.assertEqual(len(expected["results"]), 0)

    # TODO add pagination test


class RetrieveOptionTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_option_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_option_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_option_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -------------------------------
    # --- Test Retrieve An Option ---
    # -------------------------------

    def test_retrieve_option(self):
        # request
        response = self.client.get(
            reverse("option-detail", kwargs={"pk": self.option.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "option_name",
                "updated_at",
                "created_at",
            },
        )

    def test_retrieve_option_404(self):
        response = self.client.get(reverse("option-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
