from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.review.review_factory import ReviewFactory


class CreateReviewTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_create_review_by_admin(self):
        payload = {
            "message": "test review",
        }
        response = self.client.post(
            path=reverse(viewname="review-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_reviews_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(path=reverse(viewname="review-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_reviews_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(path=reverse(viewname="review-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------------
    # --- Test Create An Review ---
    # --------------------------------
    def test_create_review(self):
        # request
        payload = {
            "message": "test review",
        }
        response = self.client.post(
            path=reverse(viewname="review-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 6)
        self.assertEqual(expected["message"], payload["message"])

    def test_create_review_if_is_empty(self):
        # request
        payload = {"message": ""}
        response = self.client.post(
            path=reverse(viewname="review-list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
