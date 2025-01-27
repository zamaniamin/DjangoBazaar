from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import APITestCaseMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class ListCategoryTestMixin(APITestCaseMixin):
    def setUp(self):
        self.set_admin_user_authorization()

    # ----------------------
    # --- Helper Methods ---
    # ----------------------

    def list_category(self):
        """Helper method to list category and return the response"""
        return self.client.get(reverse("category-list"))

    def validate_category_list_response(self, response):
        """Helper method to validate the category list response."""
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        categories_list = expected["results"]
        self.assertIsInstance(categories_list, list)
        self.assertEqual(len(categories_list), 2)
        for category in categories_list:
            self.assertEqual(
                set(category.keys()),
                {
                    "id",
                    "created_at",
                    "updated_at",
                    "name",
                    "slug",
                    "description",
                    "image",
                    "parent",
                },
            )

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_list_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.list_category()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.list_category()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -----------------------------
    # --- Test List Categories ----
    # -----------------------------

    def test_list(self):
        # create a list of categories
        CategoryFactory.create_categories_list()

        # request
        response = self.list_category()
        self.validate_category_list_response(response)

    def test_list_empty(self):
        # request
        response = self.list_category()
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


class RetrieveOptionTestMixin(APITestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.view_name = "category-detail"
        cls.category = CategoryFactory.create_category()

    # ----------------------
    # --- Helper Methods ---
    # ----------------------

    def get_category(self):
        return self.client.get(reverse(self.view_name, kwargs={"pk": self.category.id}))

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.get_category()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.get_category()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --------------------------------
    # --- Test Retrieve a Category ---
    # --------------------------------

    def test_retrieve(self):
        # request
        response = self.get_category()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "created_at",
                "updated_at",
                "name",
                "slug",
                "description",
                "image",
                "parent",
            },
        )

    def test_retrieve_category_if_not_exist(self):
        response = self.client.get(reverse(self.view_name, kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
