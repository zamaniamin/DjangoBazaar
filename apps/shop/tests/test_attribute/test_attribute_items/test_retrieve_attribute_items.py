from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class ListAttributeItemsTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_with_items(
            attribute_name="test attribute", item_count=2
        )
        cls.attribute_items = cls.attribute.items.all()

    def api_path(self) -> str:
        return reverse(
            "attributes:items",
            kwargs={"attribute_id": self.attribute.id},
        )

    def validate_response_body(
        self, response, payload: dict = None, item_list_len: int = 0
    ):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response_body), item_list_len)
        for item in self.response_body:
            self.assertEqual(
                set(item.keys()),
                {
                    "id",
                    "item_name",
                },
            )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_list(self):
        response = self.send_request()
        self.validate_response_body(response, item_list_len=2)

    def test_list_if_attribute_not_exist(self):
        response = self.send_request(
            reverse("attributes:items", kwargs={"attribute_id": 999})
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_list_if_attribute_dont_have_item(self):
        attribute = AttributeFactory()
        response = self.send_request(
            reverse("attributes:items", kwargs={"attribute_id": attribute.id})
        )
        self.validate_response_body(response)


class RetrieveAttributeItemsTest(APIGetTestCaseMixin):
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
                "attribute_id": self.attribute.id,
                "pk": self.attribute_item.id,
            },
        )

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertEqual(
            set(self.response_body.keys()),
            {
                "id",
                "item_name",
            },
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve(self):
        response = self.send_request()
        self.validate_response_body(response)

    def test_retrieve_if_attribute_not_exist(self):
        response = self.send_request(
            reverse(
                "attributes:item",
                kwargs={"attribute_id": 999, "pk": self.attribute_item.id},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_retrieve_if_item_not_exist(self):
        response = self.send_request(
            reverse(
                "attributes:item",
                kwargs={"attribute_id": self.attribute.id, "pk": 999},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
