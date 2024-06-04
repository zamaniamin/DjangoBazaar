from django_filters.rest_framework import FilterSet

from apps.shop.models import Option


class OptionFilter(FilterSet):
    class Meta:
        model = Option
        fields = {
            "option_name": ["exact"],
        }
