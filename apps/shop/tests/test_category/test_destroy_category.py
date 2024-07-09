from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class DestroyCategoryTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()
        self.category = CategoryFactory.create_category()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    def test_delete_category_by_admin(self):
        response = self.client.delete(
            reverse("category-detail", kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_category_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            reverse("category-detail", kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.delete(
            reverse("category-detail", kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------
    # --- Test Delete Category ---
    # ----------------------------

    def test_delete_category(self):
        # request for delete an category
        response = self.client.delete(
            reverse("category-detail", kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # assert category is removed
        response = self.client.get(
            reverse("category-detail", kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_category_if_not_exist(self):
        response = self.client.delete(
            reverse("category-detail", kwargs={"pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_parent_category(self):
        """
        test destroy category and check the parent field of children is set to null
        """

        # make a family
        parent = self.category
        child_1, child_2 = CategoryFactory.create_categories_list()
        child_1.parent = parent
        child_2.parent = parent
        child_1.save()
        child_2.save()

        # request
        response = self.client.delete(
            reverse("category-detail", kwargs={"pk": parent.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Reload the children from the database to get the latest state
        child_1.refresh_from_db()
        child_2.refresh_from_db()

        # expected
        self.assertIsNone(child_1.parent)
        self.assertIsNone(child_2.parent)
