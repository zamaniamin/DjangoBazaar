from rest_framework import serializers

from apps.shop.models.attribute import (
    Attribute,
    AttributeItem,
)


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = "__all__"


class AttributeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeItem
        fields = ["id", "item_name"]
