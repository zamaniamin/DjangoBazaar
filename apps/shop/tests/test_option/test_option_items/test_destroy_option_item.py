from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APIDeleteTestCaseMixin
from apps.shop.demo.factory.option.option_factory import OptionFactory


class DestroyOptionItemsTest(APIDeleteTestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()
        cls.option_item = OptionFactory.add_one_option_item(cls.option.id)

    def api_path(self) -> str:
        return reverse(
            "options:item",
            kwargs={"option_id": self.option.id, "pk": self.option_item.id},
        )

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_delete(self):
        response = self.send_request()
        self.assertHTTPStatusCode(response)

        # check that option item was deleted
        response = self.client.get(self.api_path())
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_delete_with_invalid_option_id(self):
        response = self.send_request(
            reverse(
                "options:item",
                kwargs={"option_id": 999, "pk": self.option_item.id},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)

    def test_delete_with_invalid_item_pk(self):
        response = self.send_request(
            reverse(
                "options:item",
                kwargs={"option_id": self.option.id, "pk": 999},
            )
        )
        self.assertHTTPStatusCode(response, status.HTTP_404_NOT_FOUND)
