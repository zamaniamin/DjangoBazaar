from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIDeleteTestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class DestroyAttributeItemTest(APIDeleteTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_with_items(
            attribute_name="test attribute"
        )
        cls.attribute_item = cls.attribute.items.first()

    def api_path(self) -> str:
        return reverse(
            "attributes:item",
            kwargs={
                "attribute_pk": self.attribute.id,
                "pk": self.attribute_item.id,
            },
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_delete(self):
        response = self.send_request()
        self.assertHTTPStatusCode(response)

        # check that attribute item was deleted
        response = self.client.get(
            reverse(
                "attributes:item",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_delete_if_attribute_not_exist(self):
        response = self.send_request(
            reverse(
                "attributes:item",
                kwargs={"attribute_pk": 999, "pk": self.attribute_item.id},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_delete_if_item_not_exist(self):
        response = self.send_request(
            reverse(
                "attributes:item",
                kwargs={"attribute_pk": self.attribute.id, "pk": 999},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
