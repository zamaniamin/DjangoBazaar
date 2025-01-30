from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIUpdateTestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class UpdateAttributeTest(APIUpdateTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_attribute()

    def api_path(self) -> str:
        return reverse(
            "attribute-detail",
            kwargs={"pk": self.attribute.id},
        )

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "attribute_name",
                "created_at",
                "updated_at",
            },
        )
        self.assertEqual(
            self.response_body["attribute_name"], payload["attribute_name"]
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_update(self):
        payload = {"attribute_name": "new attribute"}
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_update_404(self):
        response = self.send_request(
            path=reverse("attribute-detail", kwargs={"pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
