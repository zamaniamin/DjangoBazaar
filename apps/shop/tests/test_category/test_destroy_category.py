from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import APITestCaseMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class DestroyCategoryTestMixin(APITestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.view_name = "category-detail"

    def setUp(self):
        self.set_admin_user_authorization()
        self.category = CategoryFactory.create_category()

    # ----------------------
    # --- Helper Methods ---
    # ----------------------

    def delete_category(self):
        """Helper method to delete category and return the response"""
        return self.client.delete(
            reverse(self.view_name, kwargs={"pk": self.category.id})
        )

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_delete_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.delete_category()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.delete_category()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------
    # --- Test Delete Category ---
    # ----------------------------

    def test_delete(self):
        # request for delete an category
        response = self.delete_category()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # assert category is removed
        response = self.client.get(
            reverse(self.view_name, kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_if_not_exist(self):
        response = self.client.delete(reverse(self.view_name, kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_parent(self):
        """test destroy category and check the parent field of children is set to null"""

        # make a family
        parent = self.category
        child_1, child_2 = CategoryFactory.create_categories_list()
        child_1.parent = parent
        child_2.parent = parent
        child_1.save()
        child_2.save()

        # request
        response = self.client.delete(reverse(self.view_name, kwargs={"pk": parent.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Reload the children from the database to get the latest state
        child_1.refresh_from_db()
        child_2.refresh_from_db()

        # expected
        self.assertIsNone(child_1.parent)
        self.assertIsNone(child_2.parent)
