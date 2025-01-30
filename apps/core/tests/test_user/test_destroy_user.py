from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from apps.core.tests.mixin import APIDeleteTestCaseMixin


class DestroyUserTest(APIDeleteTestCaseMixin):
    def api_path(self) -> str:
        return reverse("user-detail", kwargs={"pk": self.regular_user.id})

    def test_access_permission_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_access_permission_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_delete(self):
        response = self.send_request(

        )
        self.expected_status_code(response)
        with self.assertRaises(ObjectDoesNotExist):
            get_user_model().objects.get(id=self.regular_user.id)
