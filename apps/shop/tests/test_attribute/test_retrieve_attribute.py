from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class ListAttributeTest(APIGetTestCaseMixin):
    def api_path(self) -> str:
        return reverse("attribute-list")

    def validate_response_body(
        self, response, payload: dict = None, results_len: int = 0
    ):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response), 4)
        self.assertEqual(
            set(self.response.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )
        attribute_list = self.response["results"]
        self.assertIsInstance(attribute_list, list)
        self.assertEqual(len(attribute_list), results_len)
        for attribute in attribute_list:
            self.assertEqual(
                set(attribute.keys()),
                {
                    "id",
                    "attribute_name",
                    "created_at",
                    "updated_at",
                },
            )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_list(self):
        AttributeFactory.create_attribute_list()
        response = self.send_request()
        self.validate_response_body(response, results_len=2)

    def test_list_is_empty(self):
        response = self.send_request()
        self.validate_response_body(response)


# TODO add pagination test


class RetrieveAttributeTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_attribute()

    def api_path(self) -> str:
        return reverse("attribute-detail", kwargs={"pk": self.attribute.id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertEqual(
            set(self.response.keys()),
            {
                "id",
                "attribute_name",
                "created_at",
                "updated_at",
            },
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve(self):
        response = self.send_request()
        self.validate_response_body(response)

    def test_retrieve_404(self):
        response = self.send_request(reverse("attribute-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
