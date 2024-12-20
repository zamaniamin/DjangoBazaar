import os

from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import ProductMedia
from apps.shop.serializers.product_serializers import ProductImageSerializer
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase
from config import settings


class ProductImageUploadTest(ProductBaseTestCase):
    files: list

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.files = cls.generate_list_photo_files()
        cls.file_count = len(cls.files)

    def setUp(self):
        self.set_admin_user_authorization()
        self.active_product = ProductFactory.create_product()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_images_upload_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.post(
            reverse(
                "product-images-list",
                kwargs={"product_pk": self.active_product.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_images_upload_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.post(
            reverse(
                "product-images-list",
                kwargs={"product_pk": self.active_product.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------------
    # --- Test Upload Product Image ---
    # ---------------------------------

    def test_upload_multi_image(self):
        # request
        payload = {"images": self.files}
        response = self.post_multipart(
            reverse(
                "product-images-list", kwargs={"product_pk": self.active_product.id}
            ),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), self.file_count)

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
        product_media = ProductMedia.objects.filter(product=self.active_product)
        self.assertEqual(product_media.count(), self.file_count)

        # Check if the response data matches the serialized ProductMedia
        expected_data = ProductImageSerializer(product_media, many=True).data
        actual_data = response.data
        self.assertEqual(actual_data, expected_data)

    def test_upload_multi_image_with_is_main(self):
        # request
        payload = {"images": self.files, "is_main": True}
        response = self.post_multipart(
            reverse(
                "product-images-list", kwargs={"product_pk": self.active_product.id}
            ),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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
        product_media = ProductMedia.objects.filter(product=self.active_product)
        self.assertEqual(product_media.count(), self.file_count)

        # Check if the response data matches the serialized ProductMedia
        expected_data = ProductImageSerializer(product_media, many=True).data
        actual_data = response.data
        self.assertEqual(actual_data, expected_data)

    def test_upload_one_image(self):
        # request
        payload = {"images": self.files[0]}
        response = self.post_multipart(
            reverse(
                "product-images-list", kwargs={"product_pk": self.active_product.id}
            ),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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
        product_media = ProductMedia.objects.filter(product=self.active_product)
        self.assertEqual(product_media.count(), 1)

        # Check if the response data matches the serialized ProductMedia
        expected_data = ProductImageSerializer(product_media, many=True).data
        actual_data = response.data
        self.assertEqual(actual_data, expected_data)

    def test_upload_one_image_with_is_main(self):
        # request
        payload = {"images": self.files[0], "is_main": True}
        response = self.post_multipart(
            reverse(
                "product-images-list", kwargs={"product_pk": self.active_product.id}
            ),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
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
        # request, upload a main image
        payload = {"images": self.files[1], "is_main": True}
        response = self.post_multipart(
            reverse(
                "product-images-list", kwargs={"product_pk": self.active_product.id}
            ),
            payload,
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        old_main_image_id = expected[0]["id"]

        # request, upload second main image
        payload = {"images": self.files[0], "is_main": True}
        response2 = self.post_multipart(
            reverse(
                "product-images-list", kwargs={"product_pk": self.active_product.id}
            ),
            payload,
        )
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
