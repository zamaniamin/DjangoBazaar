from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class ListCategoryTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_list_categories_by_admin(self):
        response = self.client.get(path=reverse(viewname="category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_categories_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(path=reverse(viewname="category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_categories_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(path=reverse(viewname="category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -----------------------------
    # --- Test List Categories ----
    # -----------------------------

    def test_list_categories(self):
        # create a list of categories
        CategoryFactory.create_categories_list()

        # request
        response = self.client.get(path=reverse(viewname="category-list"))
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

        categories_list = expected["results"]
        self.assertIsInstance(categories_list, list)
        self.assertEqual(len(categories_list), 2)

        for option in categories_list:
            self.assertEqual(
                set(option.keys()),
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

    def test_list_empty(self):
        # request
        response = self.client.get(path=reverse(viewname="category-list"))
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
        cls.category = CategoryFactory.create_category()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_category_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            path=reverse(viewname="category-detail", kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_category_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            path=reverse(viewname="category-detail", kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_category_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            path=reverse(viewname="category-detail", kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --------------------------------
    # --- Test Retrieve a Category ---
    # --------------------------------

    def test_retrieve_category(self):
        # request
        response = self.client.get(
            path=reverse(viewname="category-detail", kwargs={"pk": self.category.id})
        )
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
        response = self.client.get(
            path=reverse(viewname="category-detail", kwargs={"pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
