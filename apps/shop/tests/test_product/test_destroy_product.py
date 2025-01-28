from django.urls import reverse

from apps.core.tests.mixin import APIDeleteTestCaseMixin
from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.tests.test_product.mixin import _ProductAssertMixin


class DestroyProductTest(APIDeleteTestCaseMixin, _ProductAssertMixin):
    def setUp(self):
        super().setUp()
        self.product = ProductFactory.create_product()

    def api_path(self) -> str:
        return reverse("product-detail", kwargs={"pk": self.product.id})

    def test_delete(self):
        response = self.send_request()
        self.expected_status_code(response)

# TODO test destroy a product deletes all related information too
