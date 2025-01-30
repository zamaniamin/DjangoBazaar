from django.urls import reverse

from apps.core.tests.mixin import APIUpdateTestCaseMixin
from apps.shop.demo.factory.product.product_factory import ProductFactory


class UpdateVariantTest(APIUpdateTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.product = ProductFactory.create_product(is_variable=True, has_images=True)
        cls.variant_id = cls.product.variants.first().id

    def api_path(self) -> str:
        return reverse("variant-detail", kwargs={"pk": self.variant_id})

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(self.response_body["price"], payload.get("price"))
        self.assertEqual(self.response_body["stock"], payload.get("stock"))

    def test_update(self):
        payload = {
            "price": 11,
            "stock": 111,
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_update_assign_image(self):
        product_image_id = self.product.media.first().id
        product_image_src = self.product.media.first().src
        payload = {
            "price": 11,
            "stock": 111,
            "images_id": [product_image_id],
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

        for image in self.response_body["images"]:
            self.assertEqual(image["image_id"], product_image_id)
            self.assertIn(str(product_image_src), image["src"])


# todo test_update_assign_multi_image
# TODO add partial update too
# TODO add access permission
# TODO test with multi scenario
