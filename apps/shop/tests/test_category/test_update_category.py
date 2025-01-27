from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status

from apps.core.tests.mixin import APITestCaseMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class UpdateCategoryTestMixin(APITestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.view_name = "category-detail"
        cls.category = CategoryFactory.create_category()
        cls.simple_cat_1, cls.simple_cat_2 = CategoryFactory.create_categories_list()

    def setUp(self):
        self.set_admin_user_authorization()

    # ----------------------
    # --- Helper Methods ---
    # ----------------------

    def update_category(self, payload):
        """Helper method to update category and return the response"""
        return self.put_json(
            reverse(self.view_name, kwargs={"pk": self.category.id}), payload
        )

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_update_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.update_category({})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.update_category({})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------
    # --- Test Update Category ---
    # ----------------------------

    def test_update_name(self):
        # get old category name
        old_category_name = self.category.name
        new_category_name = "new category name"
        self.assertNotEqual(old_category_name, new_category_name)

        # request
        payload = {"name": new_category_name}
        response = self.update_category(payload)

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
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
        self.assertEqual(expected["name"], new_category_name)

    def test_update_all_fields(self):
        # request
        payload = {
            "name": "new category name",
            "slug": "new-category-name",
            "description": "anything",
            "parent": self.simple_cat_2.id,
        }
        response = self.update_category(payload)

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(
            expected["slug"],
            payload.get("slug", slugify(payload["name"], allow_unicode=True)),
        )
        self.assertEqual(expected["description"], payload["description"])
        self.assertEqual(expected["parent"], payload["parent"])

    def test_update_cant_be_parent_of_itself(self):
        payload = {"parent": self.category.id}
        response = self.update_category(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_if_not_exist(self):
        payload = {"name": "new category"}
        response = self.client.put(reverse(self.view_name, kwargs={"pk": 999}), payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
