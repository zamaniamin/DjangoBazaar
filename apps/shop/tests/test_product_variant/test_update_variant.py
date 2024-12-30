import json

from django.urls import reverse
from rest_framework import status

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class UpdateVariantTest(ProductBaseTestCase):
    product = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.product = ProductFactory.create_product(is_variable=True, has_images=True)
        cls.variant_id = cls.product.variants.first().id

    def setUp(self):
        self.set_admin_user_authorization()

    def test_update_variant(self):
        self.set_admin_user_authorization()

        # request
        payload = {
            "price": 11,
            "stock": 111,
        }
        response = self.client.put(
            reverse("variant-detail", kwargs={"pk": self.variant_id}),
            json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["price"], 11)
        self.assertEqual(expected["stock"], 111)

    def test_update_assign_image(self):
        # get image id and add it to images list
        product_image_id = self.product.media.first().id
        product_image_src = self.product.media.first().src
        # images = list(self.product.media.all())

        # request
        payload = {
            "price": 11,
            "stock": 111,
            "images_id": [product_image_id],
        }
        response = self.put_json(
            reverse("variant-detail", kwargs={"pk": self.variant_id}), payload
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(expected["price"], 11)
        self.assertEqual(expected["stock"], 111)

        for image in expected["images"]:
            self.assertEqual(image["image_id"], product_image_id)
            self.assertIn(str(product_image_src), image["src"])


# todo test_update_assign_multi_image
# TODO add partial update too
# TODO add access permission
# TODO test with multi scenario
