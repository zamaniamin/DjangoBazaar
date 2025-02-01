from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status

from apps.core.tests.mixin import APIUpdateTestCaseMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class UpdateCategoryTest(APIUpdateTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = CategoryFactory()
        cls.simple_cat_1 = CategoryFactory()
        cls.simple_cat_2 = CategoryFactory()

    def api_path(self) -> str:
        return reverse("category-detail", kwargs={"pk": self.category.id})

    def validate_response_body(self, response, payload):
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
                "parents_hierarchy",
                "children_hierarchy",
            },
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_update_name(self):
        # get old category name
        old_category_name = self.category.name
        new_category_name = "new category name"
        self.assertNotEqual(old_category_name, new_category_name)

        payload = {"name": new_category_name}
        response = self.send_request(payload)
        self.validate_response_body(response, payload)
        self.assertEqual(self.response_body["name"], new_category_name)

    def test_update_all_fields(self):
        payload = {
            "name": "new category name",
            "slug": "new-category-name",
            "description": "anything",
            "parent": self.simple_cat_2.id,
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)
        self.assertEqual(self.response_body["name"], payload["name"])
        self.assertEqual(
            self.response_body["slug"],
            payload.get("slug", slugify(payload["name"], allow_unicode=True)),
        )
        self.assertEqual(self.response_body["description"], payload["description"])
        self.assertEqual(self.response_body["parent"], payload["parent"])

    def test_update_cant_be_parent_of_itself(self):
        payload = {"parent": self.category.id}
        response = self.send_request(payload)
        self.assertHTTPStatusCode(response, status.HTTP_400_BAD_REQUEST)

    def test_update_if_category_not_exist(self):
        payload = {"name": "new category"}
        response = self.send_request(
            payload, reverse("category-detail", kwargs={"pk": 999})
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
