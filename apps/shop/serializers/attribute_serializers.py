from rest_framework import serializers

from apps.core.serializers.timestamped_serializer import TimestampedSerializer
from apps.shop.models.attribute import (
    Attribute,
    AttributeItem,
)


class AttributeSerializer(TimestampedSerializer):
    class Meta:
        model = Attribute
        fields = "__all__"


class AttributeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeItem
        fields = ["id", "item_name"]
