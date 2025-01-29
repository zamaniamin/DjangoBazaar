from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIUpdateTestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class UpdateAttributeItemTest(APIUpdateTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_attribute()
        cls.item = AttributeFactory.add_one_attribute_item(cls.attribute.id)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def api_path(self) -> str:
        return reverse(
            "attribute-items-detail",
            kwargs={"attribute_pk": self.attribute.id, "pk": self.item.id},
        )

    def validate_response_body(self, response, payload):
        super().validate_response_body(response, payload)
        self.assertEqual(
            set(self.response.keys()),
            {
                "id",
                "item_name",
            },
        )
        self.assertEqual(self.response["item_name"], payload.get("item_name"))

    def test_update(self):
        payload = {"item_name": "item name 2"}
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_update_if_item_not_exist(self):
        response = self.send_request(
            path=reverse(
                "attribute-items-detail",
                kwargs={"attribute_pk": self.attribute.id, "pk": 999},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_if_attribute_not_exist(self):
        response = self.send_request(
            path=reverse(
                "attribute-items-detail",
                kwargs={"attribute_pk": 99999, "pk": self.item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
