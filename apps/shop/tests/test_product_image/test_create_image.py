import os

from django.urls import reverse

from apps.core.demo.factory.image.image_factory import ImageFactory
from apps.core.tests.mixin import APIPostTestCaseMixin, APIAssertMixin
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models.product import ProductImage
from apps.shop.serializers.product_serializers import ProductImageSerializer
from config import settings


class ProductImageUploadTest(APIPostTestCaseMixin, APIAssertMixin):
    files: list

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.files = ImageFactory.generate_list_photo_files()
        cls.file_count = len(cls.files)

    def setUp(self):
        super().setUp()
        self.active_product = ProductFactory()

    def api_path(self) -> str:
        return reverse("products:images", kwargs={"product_id": self.active_product.id})

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertIsInstance(self.response_body, list)
        self.assertEqual(len(self.response_body), self.file_count)

        for image in self.response_body:
            self.assertIsInstance(image["id"], int)
            self.assertEqual(image["product_id"], self.active_product.id)
            self.assertTrue(image["src"].strip())
            self.assertIsNone(image["alt"])
            self.assertFalse(image["is_main"])
            self.assertDatetimeFormat(image["created_at"])
            self.assertDatetimeFormat(image["updated_at"])

            # check the fie was saved
            file_path = os.path.abspath(str(settings.BASE_DIR) + image["src"])
            self.assertTrue(os.path.exists(file_path))

        # Check if the images have been added to the product
        product_media = ProductImage.objects.filter(product=self.active_product)
        self.assertEqual(product_media.count(), self.file_count)

        # Check if the response data matches the serialized ProductMedia
        expected_data = ProductImageSerializer(product_media, many=True).data
        actual_data = response.data
        self.assertEqual(actual_data, expected_data)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_upload_multi_image(self):
        payload = {"images": self.files}
        response = self.send_multipart_request(payload)
        self.validate_response_body(response, payload)

    def test_upload_multi_image_with_is_main(self):
        payload = {"images": self.files, "is_main": True}
        response = self.send_multipart_request(payload)
        self.assertHTTPStatusCode(response)

        # expected
        expected = response.json()
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), self.file_count)
        for i, image in enumerate(expected):
            self.assertIsInstance(image["id"], int)
            self.assertEqual(image["product_id"], self.active_product.id)
            self.assertTrue(image["src"].strip())
            self.assertIsNone(image["alt"])
            if i == 0:
                self.assertTrue(image["is_main"])
            else:
                self.assertFalse(image["is_main"])
            self.assertDatetimeFormat(image["created_at"])
            self.assertDatetimeFormat(image["updated_at"])

            # check the fie was saved
            file_path = os.path.abspath(str(settings.BASE_DIR) + image["src"])
            self.assertTrue(os.path.exists(file_path))

        # Check if the images have been added to the product
        product_media = ProductImage.objects.filter(product=self.active_product)
        self.assertEqual(product_media.count(), self.file_count)

        # Check if the response data matches the serialized ProductMedia
        expected_data = ProductImageSerializer(product_media, many=True).data
        actual_data = response.data
        self.assertEqual(actual_data, expected_data)

    def test_upload_one_image(self):
        payload = {"images": self.files[0]}
        response = self.send_multipart_request(payload)
        self.assertHTTPStatusCode(response)

        # expected
        expected = response.json()
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), 1)
        for image in expected:
            self.assertIsInstance(image["id"], int)
            self.assertEqual(image["product_id"], self.active_product.id)
            self.assertTrue(image["src"].strip())
            self.assertIsNone(image["alt"])
            self.assertFalse(image["is_main"])
            self.assertDatetimeFormat(image["created_at"])
            self.assertDatetimeFormat(image["updated_at"])

            # check the fie was saved
            file_path = os.path.abspath(str(settings.BASE_DIR) + image["src"])
            self.assertTrue(os.path.exists(file_path))

        # Check if the images have been added to the product
        product_media = ProductImage.objects.filter(product=self.active_product)
        self.assertEqual(product_media.count(), 1)

        # Check if the response data matches the serialized ProductMedia
        expected_data = ProductImageSerializer(product_media, many=True).data
        actual_data = response.data
        self.assertEqual(actual_data, expected_data)

    def test_upload_one_image_with_is_main(self):
        payload = {"images": self.files[0], "is_main": True}
        response = self.send_multipart_request(payload)
        self.assertHTTPStatusCode(response)

        # expected
        expected = response.json()
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), 1)
        for image in expected:
            self.assertIsInstance(image["id"], int)
            self.assertEqual(image["product_id"], self.active_product.id)
            self.assertTrue(image["src"].strip())
            self.assertIsNone(image["alt"])
            self.assertTrue(image["is_main"])
            self.assertDatetimeFormat(image["created_at"])
            self.assertDatetimeFormat(image["updated_at"])

            # check the fie was saved
            file_path = os.path.abspath(str(settings.BASE_DIR) + image["src"])
            self.assertTrue(os.path.exists(file_path))

    def test_upload_one_main_image_with_existing_main_image(self):
        """test upload a main image for product, if there was a main image befor"""
        payload = {"images": self.files[1], "is_main": True}
        response = self.send_multipart_request(payload)
        self.assertHTTPStatusCode(response)

        # expected
        expected = response.json()
        old_main_image_id = expected[0]["id"]

        # request, upload second main image
        payload = {"images": self.files[0], "is_main": True}
        response2 = self.send_multipart_request(payload)
        expected2 = response2.json()
        self.assertIsInstance(expected2, list)
        self.assertEqual(len(expected2), 2)
        for image in expected2:
            if image["id"] == old_main_image_id:
                self.assertFalse(image["is_main"])
            else:
                self.assertTrue(image["is_main"])


# TODO test update image
# TODO test delete image
