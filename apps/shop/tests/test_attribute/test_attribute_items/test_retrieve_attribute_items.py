from django.urls import reverse
from rest_framework import status

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.attribute.attribute_factory import AttributeFactory


class ListAttributeItemsTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.attribute = AttributeFactory.create_attribute()
        cls.attribute_items = AttributeFactory.add_attribute_item_list(cls.attribute.id)

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_list_items_by_admin(self):
        response = self.client.get(
            reverse(
                "attribute-items-list",
                kwargs={"attribute_pk": self.attribute.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_items_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse(
                "attribute-items-list",
                kwargs={"attribute_pk": self.attribute.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_items_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse(
                "attribute-items-list",
                kwargs={"attribute_pk": self.attribute.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -----------------------
    # --- Test List Items ---
    # -----------------------

    def test_list_items(self):
        # make request
        response = self.client.get(
            reverse(
                "attribute-items-list",
                kwargs={"attribute_pk": self.attribute.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected_attribute_items = response.json()
        self.assertEqual(len(expected_attribute_items), len(self.attribute_items))

        for item in expected_attribute_items:
            self.assertEqual(
                set(item.keys()),
                {
                    "id",
                    "item_name",
                },
            )

    def test_list_items_if_attribute_not_exist(self):
        response = self.client.get(
            reverse("attribute-items-list", kwargs={"attribute_pk": 999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_items_if_attribute_dont_have_item(self):
        # create an attribute without items
        attribute = AttributeFactory.create_attribute("material")

        # request
        response = self.client.get(
            reverse(
                "attribute-items-list", kwargs={"attribute_pk": attribute.id}
            )
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 0)


class RetrieveAttributeItemTest(CoreBaseTestCase):
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

    def test_retrieve_item_by_admin(self):
        response = self.client.get(
            reverse(
                "attribute-items-detail",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_item_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.get(
            reverse(
                "attribute-items-detail",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_item_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.get(
            reverse(
                "attribute-items-detail",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -----------------------------
    # --- Test Retrieve an Item ---
    # -----------------------------

    def test_retrieve_item(self):
        response = self.client.get(
            reverse(
                "attribute-items-detail",
                kwargs={
                    "attribute_pk": self.attribute.id,
                    "pk": self.attribute_item.id,
                },
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # expected
        expected = response.json()
        self.assertEqual(
            set(expected.keys()),
            {
                "id",
                "item_name",
            },
        )

    def test_retrieve_item_if_attribute_not_exist(self):
        response = self.client.get(
            reverse(
                "attribute-items-detail",
                kwargs={"attribute_pk": 999, "pk": self.attribute_item.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_item_if_item_not_exist(self):
        response = self.client.get(
            reverse(
                "attribute-items-detail",
                kwargs={"attribute_pk": self.attribute.id, "pk": 999},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
