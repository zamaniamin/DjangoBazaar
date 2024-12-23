from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class CategoryImageUploadTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.image_file = cls.generate_single_photo_file()

    def setUp(self):
        self.set_admin_user_authorization()
        self.category = CategoryFactory.create_category()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_upload_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.post_multipart(
            reverse(
                "category-image-list",
                kwargs={"category_pk": self.category.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.post_multipart(
            reverse(
                "category-image-list",
                kwargs={"category_pk": self.category.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------------
    # --- Test Upload Image ---
    # -------------------------

    def test_upload_image(self):
        # request
        payload = {"src": self.image_file}
        response = self.post_multipart(
            reverse("category-image-list", kwargs={"category_pk": self.category.id}),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected, dict)
        self.assertEqual(len(expected), 6)
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["category_id"], self.category.id)
        self.assertImageSrcPattern(expected["src"])
        self.assertIsNone(expected["alt"])
        self.assertDatetimeFormat(expected["updated_at"])
        self.assertDatetimeFormat(expected["created_at"])
        self.assertImageFileDirectory(expected["src"])

    def test_upload_image_with_alt(self):
        # request
        payload = {
            "src": self.image_file,
            "alt": "test alt",
        }
        response = self.post_multipart(
            reverse("category-image-list", kwargs={"category_pk": self.category.id}),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected, dict)
        self.assertEqual(len(expected), 6)
        self.assertIsInstance(expected["id"], int)
        self.assertEqual(expected["category_id"], self.category.id)
        self.assertImageSrcPattern(expected["src"])
        self.assertEqual(expected["alt"], payload["alt"])
        self.assertDatetimeFormat(expected["updated_at"])
        self.assertDatetimeFormat(expected["created_at"])
        self.assertImageFileDirectory(expected["src"])

    def test_upload_with_empty_src(self):
        payload = {"src": ""}
        response = self.post_multipart(
            reverse("category-image-list", kwargs={"category_pk": self.category.id}),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
