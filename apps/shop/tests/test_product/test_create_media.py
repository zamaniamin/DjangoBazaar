import os

from django.urls import reverse
from rest_framework import status

from apps.shop.faker.product_faker import ProductFaker
from apps.shop.models import ProductMedia
from apps.shop.serializers.product_serializers import ProductImageSerializer
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase
from config import settings


class RetrieveProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.active_product = ProductFaker.populate_active_product()

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {self.admin_access_token}")

    def test_images_upload_success(self):
        # --- init files ---
        files = self.generate_list_photo_files()
        file_count = len(files)

        # --- request ---
        payload = {"images": files}
        response = self.client.post(
            reverse("product-images-upload", kwargs={"pk": self.active_product.id}),
            payload,
        )

        # --- expected ---
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = response.json()
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), file_count)

        for image in expected:
            self.assertIsInstance(image["id"], int)
            self.assertEqual(image["product_id"], self.active_product.id)
            self.assertTrue(image["src"].strip())
            self.assertIsNone(image["alt"])
            self.assertDatetimeFormat(image["created_at"])
            self.assertDatetimeFormat(image["updated_at"])

            # check the fie was saved
            file_path = os.path.abspath(str(settings.BASE_DIR) + image["src"])
            self.assertTrue(os.path.exists(file_path))

        # Check if the images have been added to the product
        product_media = ProductMedia.objects.filter(product=self.active_product)
        self.assertEqual(product_media.count(), file_count)

        # Check if the response data matches the serialized ProductMedia
        expected_data = ProductImageSerializer(product_media, many=True).data
        actual_data = response.data
        self.assertEqual(actual_data, expected_data)


# TODO test access permissions
