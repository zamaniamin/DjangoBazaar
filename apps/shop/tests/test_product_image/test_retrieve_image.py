import os

from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin, APIAssertMixin
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.models.product import ProductImage
from config import settings


class RetrieveImageTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = ProductFactory.customize(has_image=True)
        cls.media_id = cls.product.media.first().id

    def api_path(self) -> str:
        return reverse(
            "products:image",
            kwargs={"product_id": self.product.id, "pk": self.media_id},
        )

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()


class ListImageTest(APIGetTestCaseMixin, APIAssertMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = ProductFactory.customize(has_image=True)

    def api_path(self) -> str:
        return reverse("products:images", kwargs={"product_id": self.product.id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)

        # expected
        image = self.response_body[0]
        self.assertIsInstance(self.response_body, list)
        # self.assertEqual(len(self.response), 4)

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
        # self.assertEqual(product_media.count(), 4)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_list_with_one_image(self):
        response = self.send_request()
        self.validate_response_body(response)

    def _test_retrieve_with_multi_images(self):
        # TODO fix this test
        active_product = ProductFactory.customize(has_image=True)
        response = self.send_request(
            reverse("products:images", kwargs={"product_id": active_product.id}),
        )

        # expected
        self.assertHTTPStatusCode(response, status.HTTP_200_OK)
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
