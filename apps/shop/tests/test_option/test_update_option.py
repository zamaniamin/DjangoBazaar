from django.urls import reverse
from rest_framework import status
from rest_framework.utils import json

from apps.core.tests.base_test import CoreBaseTestCase
from apps.shop.demo.factory.option.option_factory import OptionFactory


class UpdateOptionTest(CoreBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.option = OptionFactory.create_option()

    def setUp(self):
        self.set_admin_user_authorization()

    # -------------------------------
    # --- Test Access Permissions ---
    # -------------------------------

    def test_update_option_by_admin(self):
        # request
        payload = {"option_name": "black"}
        response = self.client.put(
            path=reverse(
                viewname="option-detail",
                kwargs={"pk": self.option.id},
            ),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_option_by_regular_user(self):
        self.set_regular_user_authorization()
        response = self.client.put(
            path=reverse(
                viewname="option-detail",
                kwargs={"pk": self.option.id},
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_option_by_anonymous_user(self):
        self.set_anonymous_user_authorization()
        response = self.client.put(
            path=reverse(
                viewname="option-detail",
                kwargs={"pk": self.option.id},
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------
    # --- Update Option ---
    # ---------------------

    def test_update_option(self):
        # get old option name
        old_option_name = self.option.option_name

        # request
        new_option_name = "color2"
        payload = {"option_name": new_option_name}
        response = self.client.put(
            path=reverse(
                viewname="option-detail",
                kwargs={"pk": self.option.id},
            ),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "option_name",
            },
        )
        self.assertEqual(expected["option_name"], new_option_name)
        self.assertNotEqual(old_option_name, new_option_name)

    def test_update_if_option_not_exist(self):
        # request
        response = self.client.put(
            path=reverse(
                viewname="option-detail",
                kwargs={"pk": 999},
            ),
            content_type="application/json",
        )

        # expected
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
