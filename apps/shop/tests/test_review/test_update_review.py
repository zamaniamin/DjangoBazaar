from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.review.review_factory import ReviewFactory


class UpdateReviewTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.review = ReviewFactory.create_review()

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_update_review_by_admin(self):
        # request
        payload = {
            "message": ReviewFactory.review_message_2
        }
        response = self.client.put(
            path=reverse(
                viewname="review-detail",
                kwargs={"pk": self.review.id},
            ),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_review_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.put(
            path=reverse(
                viewname="review-detail",
                kwargs={"pk": self.review.id},
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_review_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.put(
            path=reverse(
                viewname="review-detail",
                kwargs={"pk": self.review.id},
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------
    # --- Update Review ---
    # ------------------------

    def test_update_review(self):
        # get old review name
        old_message = self.review.message

        # request
        new_message = "new message"
        payload = {"message": new_message}
        response = self.client.put(
            path=reverse(
                viewname="review-detail",
                kwargs={"pk": self.review.id},
            ),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "message",
                'rating',
                'user',
                'status',
                'product'
            },
        )
        self.assertEqual(expected["message"], new_message)
        self.assertNotEqual(old_message, new_message)

    def test_update_review_not_exist(self):
        # request
        response = self.client.put(
            path=reverse(
                viewname="review-detail",
                kwargs={"pk": 999},
            ),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
