from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.review.review_factory import ReviewFactory


class ListReviewTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_list_reviews_by_admin(self):
        response = self.client.get(path=reverse(viewname="review-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_reviews_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(path=reverse(viewname="review-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_reviews_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(path=reverse(viewname="review-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -----------------------------
    # --- Test List Reviews ----
    # -----------------------------

    def test_review_list(self):
        # create a list of reviews
        ReviewFactory.create_review_list()

        # request
        response = self.client.get(path=reverse(viewname="review-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )

        review_list = expected["results"]
        self.assertIsInstance(review_list, list)
        self.assertEqual(len(review_list), 2)

        for review in review_list:
            self.assertEqual(
                set(review.keys()),
                {
                    "id",
                    "message",
                    'rating',
                    'user',
                    'status',
                    'product'
                },
            )

    def test_list_is_empty(self):
        # request
        response = self.client.get(path=reverse(viewname="review-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )
        self.assertIsInstance(expected["results"], list)
        self.assertEqual(len(expected["results"]), 0)


class RetrieveReviewTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.review = ReviewFactory.create_review()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_review_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            path=reverse(viewname="review-detail", kwargs={"pk": self.review.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_review_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            path=reverse(viewname="review-detail", kwargs={"pk": self.review.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_review_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            path=reverse(viewname="review-detail", kwargs={"pk": self.review.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----------------------------------
    # --- Test Retrieve An Review ---
    # ----------------------------------

    def test_retrieve_review(self):
        # request
        response = self.client.get(
            path=reverse(viewname="review-detail", kwargs={"pk": self.review.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
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

    def test_retrieve_review_404(self):
        response = self.client.get(
            path=reverse(viewname="review-detail", kwargs={"pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
