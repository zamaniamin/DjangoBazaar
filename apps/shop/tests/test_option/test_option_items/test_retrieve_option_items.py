from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIGetTestCaseMixin
from apps.shop.demo.factory.option.option_factory import OptionFactory


class ListOptionItemsTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()
        cls.option_items = OptionFactory.add_option_item_list(cls.option.id)

    def api_path(self) -> str:
        return reverse("option-items-list", kwargs={"option_pk": self.option.id})

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response_body), len(self.option_items))
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
        self.validate_response_body(response)

    def test_list_with_invalid_option_pk(self):
        response = self.send_request(
            reverse("option-items-list", kwargs={"option_pk": 999})
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_list_if_option_dont_have_item(self):
        option = OptionFactory.create_option("material")
        response = self.send_request(
            reverse("option-items-list", kwargs={"option_pk": option.id})
        )

        # expected
        self.assertHTTPStatusCode(response)
        expected = response.json()
        self.assertEqual(len(expected), 0)


class RetrieveOptionItemTest(APIGetTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()
        cls.option_item = OptionFactory.add_one_option_item(cls.option.id)

    def api_path(self) -> str:
        return reverse(
            "option-items-detail",
            kwargs={"option_pk": self.option.id, "pk": self.option_item.id},
        )

    def validate_response_body(self, response, payload: dict = None):
        super().validate_response_body(response, payload)

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_retrieve(self):
        response = self.send_request()
        self.assertHTTPStatusCode(response)

    def test_retrieve_items_if_option_not_exist(self):
        response = self.send_request(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": 999, "pk": self.option_item.id},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_retrieve_item_if_item_not_exist(self):
        response = self.send_request(
            reverse(
                "option-items-detail",
                kwargs={"option_pk": self.option.id, "pk": 999},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
