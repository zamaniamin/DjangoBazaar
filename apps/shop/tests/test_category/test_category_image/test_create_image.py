from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APITestCaseMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class CategoryImageUploadTestMixin(APITestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.image_file = cls.generate_single_photo_file()

    def setUp(self):
        self.set_admin_user_authorization()
        self.category = CategoryFactory.create_category()

    # ----------------------
    # --- Helper Methods ---
    # ----------------------

    def upload_image(self, payload):
        """Helper method to upload an image and return the response"""
        return self.post_multipart(
            reverse("category-image-list", kwargs={"category_pk": self.category.id}),
            payload,
        )

    def validate_image_response(self, response, payload: dict = None):
        """Helper method to validate the image response."""
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected = response.json()
        self.assertIsInstance(expected, dict)
        self.assertEqual(len(expected), 6)
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["category_id"], self.category.id)
        self.assertImageSrcPattern(expected["src"])
        self.assertEqual(expected["alt"], payload["alt"] if payload else None)
        self.assertDatetimeFormat(expected["updated_at"])
        self.assertDatetimeFormat(expected["created_at"])
        self.assertImageFileDirectory(expected["src"])

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_upload_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.upload_image({})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.upload_image({})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------------
    # --- Test Upload Image ---
    # -------------------------

    def test_upload_image(self):
        payload = {"src": self.image_file}
        response = self.upload_image(payload)
        self.validate_image_response(response)

    def test_upload_image_with_alt(self):
        payload = {
            "src": self.image_file,
            "alt": "test alt",
        }
        response = self.upload_image(payload)
        self.validate_image_response(response, payload)

    def test_upload_with_empty_src(self):
        payload = {"src": ""}
        response = self.upload_image(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
