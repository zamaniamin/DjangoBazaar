from django_filters.rest_framework import FilterSet

from apps.shop.models import Product


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = [
            "status",
        ]
