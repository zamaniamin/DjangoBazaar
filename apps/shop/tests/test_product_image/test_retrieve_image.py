import os

from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models import ProductImage
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCaseMixin
from config import settings


class RetrieveImageTest(ProductBaseTestCaseMixin):
    files: list

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = ProductFactory.create_product(has_images=True)

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_retrieve_image_by_regular_user(self):
        self.set_regular_user_authorization()
        media_id = self.product.media.first().id
        response = self.client.get(
            reverse(
                "product-images-detail",
                kwargs={"product_pk": self.product.id, "pk": media_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_image_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        media_id = self.product.media.first().id
        response = self.client.get(
            reverse(
                "product-images-detail",
                kwargs={"product_pk": self.product.id, "pk": media_id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ListImageTest(ProductBaseTestCaseMixin):
    files: list

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = ProductFactory.create_product(has_images=True)

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_list_images_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("product-images-list", kwargs={"product_pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_images_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse("product-images-list", kwargs={"product_pk": self.product.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --------------------------------
    # --- Test List Product Images ---
    # --------------------------------

    def test_list_with_one_image(self):
        # request
        response = self.client.get(
            reverse("product-images-list", kwargs={"product_pk": self.product.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        image = expected[0]
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), 1)

        self.assertIsInstance(image["id"], int)
        self.assertEqual(image["product_id"], self.product.id)
        self.assertTrue(image["src"].strip())
        self.assertIsNone(image["alt"])
        self.assertDatetimeFormat(image["created_at"])
        self.assertDatetimeFormat(image["updated_at"])

        # check the fie was saved
        file_path = os.path.abspath(
            str(settings.MEDIA_ROOT) + image["src"].split("media")[1]
        )
        self.assertTrue(os.path.exists(file_path))

        # Check if the images have been added to the product
        product_media = ProductImage.objects.filter(product=self.product)
        self.assertEqual(product_media.count(), 1)

    def _test_retrieve_with_multi_images(self):
        # TODO fix this test
        # request
        active_product = ProductFactory.create_product(has_images=True)
        response = self.client.get(
            reverse("product-images-list", kwargs={"product_pk": active_product.id}),
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertIsInstance(expected, list)
        self.assertEqual(len(expected), 8)

        for image in expected:
            self.assertIsInstance(image["id"], int)
            self.assertEqual(image["product_id"], active_product.id)
            self.assertTrue(image["src"].strip())
            self.assertIsNone(image["alt"])
            self.assertDatetimeFormat(image["created_at"])
            self.assertDatetimeFormat(image["updated_at"])

            # check the fie was saved
            file_path = os.path.abspath(
                str(settings.MEDIA_ROOT) + image["src"].split("media")[1]
            )
            self.assertTrue(os.path.exists(file_path))
