from django.urls import reverse
from rest_framework import status

from apps.core.tests.mixin import APITestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class DestroyAttributeItemsTestMixin(APITestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_attribute()
        cls.attribute_item = AttributeFactory.add_one_attribute_item(cls.attribute.id)

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_delete_item_by_admin(self):
        response = self.client.delete(
            reverse(
                "attribute-items-detail",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            reverse(
                "attribute-items-detail",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.delete(
            reverse(
                "attribute-items-detail",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------
    # --- Test Delete An Item ---
    # ---------------------------

    def test_delete_item(self):
        # delete an attribute item
        response = self.client.delete(
            reverse(
                "attribute-items-detail",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # check that attribute item was deleted
        response = self.client.get(
            reverse(
                "attribute-items-detail",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_if_attribute_not_exist(self):
        response = self.client.delete(
            reverse(
                "attribute-items-detail",
                kwargs={"attribute_pk": 999, "pk": self.attribute_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_if_item_not_exist(self):
        response = self.client.delete(
            reverse(
                "attribute-items-detail",
                kwargs={"attribute_pk": self.attribute.id, "pk": 999},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
