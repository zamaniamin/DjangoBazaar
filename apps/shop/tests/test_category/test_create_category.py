from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class CreateCategoryTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()

    # ----------------------
    # --- Helper Methods ---
    # ----------------------

    def create_category(self, payload):
        """Helper method to create category and return the response"""
        return self.post_json(reverse("category-list"), payload)

    def validate_category_response(self, response, payload, parent_category=None):
        """Helper method to validate the category response."""
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected = response.json()
        self.assertEqual(len(expected), 8)
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(
            expected["slug"],
            payload.get("slug", slugify(payload["name"], allow_unicode=True)),
        )
        self.assertEqual(expected["description"], payload.get("description"))
        self.assertEqual(
            expected["parent"], parent_category.id if parent_category else None
        )
        self.assertDatetimeFormat(expected["created_at"])
        self.assertDatetimeFormat(expected["updated_at"])
        self.assertIsNone(expected["image"])

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.create_category({})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.create_category({})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------
    # --- Test Create Category ---
    # ----------------------------

    def test_create(self):
        payload = {
            "name": "test category",
        }
        response = self.create_category(payload)
        self.validate_category_response(response, payload)

    def test_create_with_all_fields(self):
        parent_category = CategoryFactory.create_category()

        payload = {
            "name": "test category",
            "slug": "test-custom-slug",
            "description": "any description",
            "parent": parent_category.id,
        }
        response = self.create_category(payload)
        self.validate_category_response(response, payload, parent_category)

    def test_create_with_persian_characters(self):
        payload = {
            "name": "دسته بندی",
        }
        response = self.create_category(payload)
        self.validate_category_response(response, payload)

    def test_create_with_empty_parent(self):
        payload = {
            "name": "test category",
            "parent": "",
        }
        response = self.create_category(payload)
        self.validate_category_response(response, payload)


# TODO test create with invalid payloads
