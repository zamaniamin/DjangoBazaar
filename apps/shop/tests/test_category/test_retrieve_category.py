from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class ListCategoryTest(APIGetTestCaseMixin):
    def api_path(self) -> str:
        return reverse("category-list")

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_list(self):
        CategoryFactory.create_categories_list()
        response = self.send_request()
        self.validate_response_body(response)
        self.assertEqual(len(self.response), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )
        categories_list = self.response["results"]
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

    def test_list_empty(self):
        response = self.send_request()
        self.validate_response_body(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.response), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )
        self.assertIsInstance(self.response["results"], list)
        self.assertEqual(len(self.response["results"]), 0)

    # TODO add pagination test


class RetrieveCategoryTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = CategoryFactory.create_category()

    def api_path(self) -> str:
        return reverse("category-detail", kwargs={"pk": self.category.id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
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

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve(self):
        response = self.send_request()
        self.validate_response_body(response)

    def test_retrieve_404(self):
        response = self.client.get(reverse("category-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
