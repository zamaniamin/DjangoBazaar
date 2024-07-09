import os
import re

from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.category.category_factory import CategoryFactory
from config import settings


class UpdateCategoryTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = CategoryFactory.create_category()
        cls.simple_cat_1, cls.simple_cat_2 = CategoryFactory.create_categories_list()
        cls.image_file = cls.generate_single_photo_file()

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_update_category_by_admin(self):
        # request
        payload = {"name": "updated category"}
        response = self.client.put(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            ),
            payload,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_category_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.put(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_category_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.put(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------
    # --- Test Update Category ---
    # ----------------------------

    def test_update_category_name(self):
        # get old category name
        old_category_name = self.category.name

        # request
        new_category_name = "new category name"
        payload = {"name": new_category_name}
        response = self.client.put(
            reverse("category-detail", kwargs={"pk": self.category.id}),
            payload,
        )

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
        self.assertNotEqual(old_category_name, new_category_name)

    def test_update_category_all_fields(self):
        # request
        payload = {
            "name": "new category name",
            "slug": "new-category-name",
            "description": "anything",
            "image": self.image_file,
            "parent": self.simple_cat_2.id,
        }
        response = self.client.put(
            reverse("category-detail", kwargs={"pk": self.category.id}),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["name"], payload["name"])
        self.assertEqual(expected["slug"], payload["slug"])
        self.assertEqual(expected["description"], payload["description"])
        self.assertEqual(expected["parent"], payload["parent"])

        # expected file is saved in media directory
        file_path = os.path.abspath(str(settings.BASE_DIR))
        extracted_path = re.search(
            pattern=r"testserver\/(.*)", string=expected["image"]
        ).group(1)
        full_file_path = os.path.join(file_path, extracted_path)
        self.assertTrue(os.path.exists(full_file_path))

    def test_update_category_cant_be_parent_of_itself(self):
        # request
        payload = {"parent": self.category.id}
        response = self.client.put(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            ),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_category_if_not_exist(self):
        # request
        payload = {"name": "new category"}
        response = self.client.put(
            reverse(
                "category-detail",
                kwargs={"pk": 999},
            ),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
