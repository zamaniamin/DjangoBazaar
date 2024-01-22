from django_filters.rest_framework import FilterSet

from apps.shop.models import Product


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            "status": ["exact"],
            "updated_at": "",
            "variants__price": ["gt", "lt"],
            "variants__stock": ["gt", "lt"],
        }
