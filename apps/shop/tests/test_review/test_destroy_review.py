from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.review.review_factory import ReviewFactory


class DestroyReviewTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.review = ReviewFactory.create_review()

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    def test_delete_review_by_admin(self):
        response = self.client.delete(
            path=reverse(viewname="review-detail", kwargs={"pk": self.review.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_review_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            path=reverse(viewname="review-detail", kwargs={"pk": self.review.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.delete(
            path=reverse(viewname="review-detail", kwargs={"pk": self.review.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -----------------------------
    # --- Test Delete Review ---
    # -----------------------------

    def test_delete_review(self):
        # request for delete an review
        response = self.client.delete(
            path=reverse(viewname="review-detail", kwargs={"pk": self.review.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # assert review is removed
        response = self.client.get(
            path=reverse(viewname="review-detail", kwargs={"pk": self.review.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_review_if_not_exist(self):
        response = self.client.delete(
            path=reverse(viewname="review-detail", kwargs={"pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
