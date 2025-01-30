from django.urls import reverse
from django.utils.text import slugify

from apps.core.tests.mixin import APIPostTestCaseMixin, APIAssertMixin
from apps.shop.demo.factory.category.category_factory import CategoryFactory


class CreateCategoryTest(APIPostTestCaseMixin, APIAssertMixin):
    def api_path(self) -> str:
        return reverse("category-list")

    def validate_response_body(self, response, payload, parent_category=None):
        super().validate_response_body(response, payload)
        self.assertEqual(len(self.response_body), 8)
        self.assertIsInstance(self.response_body["id"], int)
        self.assertEqual(self.response_body["name"], payload["name"])
        self.assertEqual(
            self.response_body["slug"],
            payload.get("slug", slugify(payload["name"], allow_unicode=True)),
        )
        self.assertEqual(self.response_body["description"], payload.get("description"))
        self.assertEqual(
            self.response_body["parent"],
            parent_category.id if parent_category else None,
        )
        self.assertDatetimeFormat(self.response_body["created_at"])
        self.assertDatetimeFormat(self.response_body["updated_at"])
        self.assertIsNone(self.response_body["image"])

    def test_create_by_regular_user(self):
        self.check_access_permission_by_regular_user()

    def test_create_by_anonymous_user(self):
        self.check_access_permission_by_anonymous_user()

    def test_create(self):
        payload = {
            "name": "test category",
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_create_with_all_fields(self):
        parent_category = CategoryFactory.create_category()
        payload = {
            "name": "test category",
            "slug": "test-custom-slug",
            "description": "any description",
            "parent": parent_category.id,
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload, parent_category)

    def test_create_with_persian_characters(self):
        payload = {
            "name": "دسته بندی",
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)

    def test_create_with_empty_parent(self):
        payload = {
            "name": "test category",
            "parent": "",
        }
        response = self.send_request(payload)
        self.validate_response_body(response, payload)


# TODO test create with invalid payloads
