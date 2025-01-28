from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIDeleteTestCaseMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class DestroyCategoryTestMixin(APIDeleteTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()
        self.category = CategoryFactory.create_category()

    def api_path(self) -> str:
        return reverse("category-detail", kwargs={"pk": self.category.id})

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_delete(self):
        response = self.send_request()
        self.expected_status_code(response)
        response = self.client.get(
            reverse("category-detail", kwargs={"pk": self.category.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_404(self):
        response = self.send_request(reverse("category-detail", kwargs={"pk": 999}))
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
