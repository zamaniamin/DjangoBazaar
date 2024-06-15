from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class DestroyAttributeTest(CoreBaseTestCase):
    def setUp(self):
        self.set_admin_user_authorization()
        self.attribute = AttributeFactory.create_attribute()
        self.attribute_item = AttributeFactory.add_one_attribute_item(self.attribute.id)

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------
    def test_delete_attribute_by_admin(self):
        response = self.client.delete(
            reverse("attribute-detail", kwargs={"pk": self.attribute.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_attribute_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.delete(
            reverse("attribute-detail", kwargs={"pk": self.attribute.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_attribute_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.delete(
            reverse("attribute-detail", kwargs={"pk": self.attribute.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------
    # --- Test Delete attribute ---
    # --------------------------

    def test_delete_attribute(self):
        # --- request for delete an attribute ---
        response = self.client.delete(
            reverse("attribute-detail", kwargs={"pk": self.attribute.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- assert attribute is removed ---
        response = self.client.get(
            reverse("attribute-detail", kwargs={"pk": self.attribute.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # --- assert attribute items are removed ---
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

    def test_delete_attribute_404(self):
        response = self.client.delete(reverse("attribute-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
