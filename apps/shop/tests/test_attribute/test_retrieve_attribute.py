from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import APITestCaseMixin
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class ListAttributeTestMixin(APITestCaseMixin):
    def setUp(self):
        self.set_admin_user_authorization()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_list_attributes_by_admin(self):
        response = self.client.get(reverse("attribute-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_attributes_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(reverse("attribute-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_attributes_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(reverse("attribute-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -----------------------------
    # --- Test List Attributes ----
    # -----------------------------

    def test_attribute_list(self):
        # create a list of attributes
        AttributeFactory.create_attribute_list()

        # request
        response = self.client.get(reverse("attribute-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )

        attribute_list = expected["results"]
        self.assertIsInstance(attribute_list, list)
        self.assertEqual(len(attribute_list), 2)

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

    def test_list_is_empty(self):
        # request
        response = self.client.get(reverse("attribute-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(
            set(response.data.keys()),
            {
                "count",
                "next",
                "previous",
                "results",
            },
        )
        self.assertIsInstance(expected["results"], list)
        self.assertEqual(len(expected["results"]), 0)

    # TODO add pagination test


class RetrieveAttributeTestMixin(APITestCaseMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_attribute()

    # ------------------------------
    # --- Test Access Permission ---
    # ------------------------------

    def test_retrieve_attribute_by_admin(self):
        self.set_admin_user_authorization()
        response = self.client.get(
            reverse("attribute-detail", kwargs={"pk": self.attribute.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_attribute_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse("attribute-detail", kwargs={"pk": self.attribute.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_attribute_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse("attribute-detail", kwargs={"pk": self.attribute.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ----------------------------------
    # --- Test Retrieve An Attribute ---
    # ----------------------------------

    def test_retrieve_attribute(self):
        # request
        response = self.client.get(
            reverse("attribute-detail", kwargs={"pk": self.attribute.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "attribute_name",
                "created_at",
                "updated_at",
            },
        )

    def test_retrieve_attribute_404(self):
        response = self.client.get(reverse("attribute-detail", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
