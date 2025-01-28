from django.urls import reverse
from rest_framework import status

from apps.core.demo.factory.image.image_factory import ImageFactory
from apps.core.tests.image_mixin import ImageTestCaseMixin
from apps.core.tests.mixin import APIPostTestCaseMixin, APIAssertMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class CategoryImageUploadTest(
    APIPostTestCaseMixin, ImageTestCaseMixin, APIAssertMixin
):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.image_file = ImageFactory.generate_single_photo_file()

    def setUp(self):
        super().setUp()
        self.category = CategoryFactory.create_category()

    def api_path(self) -> str:
        return reverse("category-image-list", kwargs={"category_pk": self.category.id})

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertIsInstance(self.response, dict)
        self.assertEqual(len(self.response), 6)
        self.assertIsInstance(self.response["id"], int)
        self.assertEqual(self.response["category_id"], self.category.id)
        self.assertImageSrcPattern(self.response["src"])
        self.assertEqual(self.response["alt"], payload.get("alt"))
        self.assertDatetimeFormat(self.response["updated_at"])
        self.assertDatetimeFormat(self.response["created_at"])
        self.assertImageFileDirectory(self.response["src"])

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_upload_image(self):
        payload = {"src": self.image_file}
        response = self.send_multipart_request(payload)
        self.validate_response_body(response, payload)

    def test_upload_image_with_alt(self):
        payload = {
            "src": self.image_file,
            "alt": "test alt",
        }
        response = self.send_multipart_request(payload)
        self.validate_response_body(response, payload)

    def test_upload_with_empty_src(self):
        payload = {"src": ""}
        response = self.send_multipart_request(payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
