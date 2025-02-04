from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin, APIAssertMixin
from apps.shop.demo.factory.option.option_factory import OptionFactory


class ListOptionTest(APIGetTestCaseMixin):
    def api_path(self) -> str:
        return reverse("option-list")

    def validate_response_body(
        self, response, payload: dict = None, result_len: int = 0
    ):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response_body), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )

        option_list = self.response_body["results"]
        self.assertIsInstance(option_list, list)
        self.assertEqual(len(option_list), result_len)

        for option in option_list:
            self.assertEqual(
                set(option.keys()),
                {
                    "id",
                    "option_name",
                    "updated_at",
                    "created_at",
                },
            )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_list(self):
        OptionFactory.create_option_list()
        response = self.send_request()
        self.validate_response_body(response, result_len=2)

    def test_empty_list(self):
        response = self.send_request()
        self.validate_response_body(response)


# TODO add pagination test


class RetrieveOptionTest(APIGetTestCaseMixin, APIAssertMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()

    def api_path(self) -> str:
        return reverse("option-detail", kwargs={"pk": self.option.id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertEqual(
            set(self.response_body.keys()),
            {
                "id",
                "option_name",
                "updated_at",
                "created_at",
            },
        )
        self.assertDatetimeFormat(self.response_body["created_at"])
        self.assertDatetimeFormat(self.response_body["updated_at"])

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve(self):
        response = self.send_request()
        self.validate_response_body(response)

    def test_retrieve_404(self):
        response = self.send_request(reverse("option-detail", kwargs={"pk": 999}))
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
