from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.shop.demo.factory.product.product_factory import ProductFactory
from apps.shop.services.product_service import ProductService
from apps.shop.demo.factory.category.category_factory import CategoryFactory
from apps.shop.models import Product
from apps.shop.tests.test_product.base_test_case import ProductBaseTestCase


class SearchProductTest(ProductBaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # create product
        (
            cls.simple_product_payload,
            cls.simple_product,
        ) = ProductFactory.create_product(get_payload=True)
        (
            cls.variable_product_payload,
            cls.variable_product,
        ) = ProductFactory.create_product(is_variable=True, get_payload=True)

        # products with different status
        cls.active_product = ProductFactory.create_product()
        cls.archived_product = ProductFactory.create_product(
            status=Product.STATUS_ARCHIVED
        )
        cls.draft_product = ProductFactory.create_product(status=Product.STATUS_DRAFT)

        # create
        cls.category1 = CategoryFactory.create_category(name="Electronics")
        cls.category2 = CategoryFactory.create_category(name="Clothing")
        product_data_1 = {
            "name": "Laptop",
            "description": "new Laptop",
            "status": Product.STATUS_ACTIVE,
            "price": 11,
            "stock": 11,
            "options": [],
            "category": cls.category1,
        }
        cls.product1 = ProductService.create_product(**product_data_1)
        product_data_2 = {
            "name": "phone",
            "description": "new phone",
            "status": Product.STATUS_ACTIVE,
            "price": 11,
            "stock": 11,
            "options": [],
            "category": cls.category1,
        }
        cls.product2 = ProductService.create_product(**product_data_2)
        product_data_3 = {
            "name": "tablet",
            "description": "new tablet",
            "status": Product.STATUS_ACTIVE,
            "price": 11,
            "stock": 11,
            "options": [],
            "category": cls.category2,
        }
        cls.product3 = ProductService.create_product(**product_data_3)

    def setUp(self):
        self.client = APIClient()

    def test_search_active_product(self):
        response = self.client.get(
            path=reverse(viewname="product-list"), data={"status": "active"}
        )
        # expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = response.json()
        self.assertEqual(len(expected), 4)
        self.assertEqual(expected["count"], 6)
        self.assertEqual(len(expected["results"]), 6)

    def test_search_by_product_name(self):
        response = self.client.get(reverse("product-list"), {"search": "Laptop"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_by_product_name_and_description(self):
        response = self.client.get(reverse("product-list"), {"search": "new"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_search_by_category_name(self):
        response = self.client.get(reverse("product-list"), {"search": "Clothing"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_by_category_name_ignore_category_description(self):
        response = self.client.get(reverse("product-list"), {"search": "Clothing"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "tablet")

    def test_search_by_product_name_description_and_category_name(self):
        response = self.client.get(
            reverse("product-list"), {"search": "Laptop new Electronics"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_by_name_description_category_name_ignore_category_description(self):
        response = self.client.get(
            reverse("product-list"), {"search": "phone latest Electronics"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(len(response.data["results"]), 1)
    def test_unicode_characters(self):
        unicode_term = "Café"
        Product.objects.create(name="Café Table", description="Stylish café table", category= self.category1)
        response = self.client.get(reverse("product-list"),{"search": "Café"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_input(self):
        response = self.client.get(reverse("product-list"),{"search": ""})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_input(self):
        response = self.client.get(reverse("product-list"),{"search": "123-"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # TODO scenario 1 : test search base on just "product name"
    # TODO scenario 2 : test search base on "product name" and "product description"
    # TODO scenario 3 : test search base on "category name"
    # TODO scenario 4 : test search base on "category name" and ignore "category description"
    # TODO scenario 5 : test search base on "product name" and "product description" and "category name"
    # TODO scenario 6 : test search base on "product name" and "product description" and "category name" and ignore "category description" ?

    # TODO scenario  : test pagination
    # TODO scenario  : test in each pagination should load 10 products (DefaultPagination.page_size)
