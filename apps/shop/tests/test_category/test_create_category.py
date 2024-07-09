import os
import re

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.category.category_factory import CategoryFactory
from config import settings


class CreateCategoryTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        # Runs once per test class.

        super().setUpTestData()
        cls.image_file = cls.generate_single_photo_file()

    def setUp(self):
        # Runs before every test method.

        # The reason you cannot call `set_admin_user_authorization()` in the `setUpTestData()` method is that
        # `setUpTestData()` is a class method and thus operates at the class level, not the instance level.
        # The `self` parameter in `set_admin_user_authorization()` refers to an instance of the test case, which is not
        # available within a class method.

        # In `setUpTestData()`, you only have access to `cls`, which is the class itself, not an instance.
        # Instance methods (like `set_admin_user_authorization`) require an instance of the class to be called.

        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_category_by_admin(self):
        payload = {
            "name": "test category",
        }
        response = self.client.post(
            reverse("category-list"), payload
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(reverse("category-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------
    # --- Test Create A Category ---
    # ------------------------------

    def test_create_category(self):
        # make request
        payload = {
            "name": "test category",
        }
        response = self.client.post(
            reverse("category-list"), payload
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 8)

        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(expected["slug"], "test-category")
        self.assertIsNone(expected["description"])
        self.assertIsNone(expected["image"])
        self.assertIsNone(expected["parent"])
        self.assertDatetimeFormat(expected["created_at"])
        self.assertDatetimeFormat(expected["updated_at"])

    def test_creat_category_with_image(self):
        # request
        payload = {"name": "test category", "image": self.image_file}
        response = self.client.post(
            reverse("category-list"), payload
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertEqual(len(expected), 8)
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(expected["slug"], "test-category")
        self.assertIsNone(expected["description"])
        self.assertTrue(expected["image"].strip())
        self.assertIsNone(expected["parent"])
        self.assertDatetimeFormat(expected["created_at"])
        self.assertDatetimeFormat(expected["updated_at"])

        # expected file is saved in media directory
        file_path = os.path.abspath(str(settings.BASE_DIR))
        extracted_path = re.search(
            pattern=r"testserver\/(.*)", string=expected["image"]
        ).group(1)
        full_file_path = os.path.join(file_path, extracted_path)
        self.assertTrue(os.path.exists(full_file_path))

    def test_create_category_with_all_fields(self):
        # create a category and use it as parent category
        parent_category = CategoryFactory.create_category()

        # make request
        payload = {
            "name": "test category",
            "image": self.generate_single_photo_file(),
            "slug": "test-custom-slug",
            "description": "any description",
            "parent": parent_category.id,
        }
        response = self.client.post(
            reverse("category-list"), payload
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 8)

        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(expected["slug"], payload["slug"])
        self.assertEqual(expected["description"], payload["description"])
        self.assertTrue(expected["image"].strip())
        self.assertEqual(expected["parent"], parent_category.id)
        self.assertDatetimeFormat(expected["created_at"])
        self.assertDatetimeFormat(expected["updated_at"])

        # expected file is saved in media directory
        file_path = os.path.abspath(str(settings.BASE_DIR))
        extracted_path = re.search(
            pattern=r"testserver\/(.*)", string=expected["image"]
        ).group(1)
        full_file_path = os.path.join(file_path, extracted_path)
        self.assertTrue(os.path.exists(full_file_path))

    def test_create_category_with_persian_characters(self):
        # make request
        payload = {
            "name": "دسته بندی",
        }
        response = self.client.post(
            reverse("category-list"), payload
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 8)
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(expected["slug"], "دسته-بندی")

# TODO test create with invalid payloads
