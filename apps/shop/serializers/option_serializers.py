from rest_framework import serializers

from apps.shop.models import (
    Option,
    OptionItem,
)


class OptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionItem
        fields = ["id", "item_name"]


class OptionSerializer(serializers.ModelSerializer):
    items = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = Option
        fields = ["id", "option_name", "items"]


