from rest_framework import serializers

from apps.core.serializers.mixin import ModelMixinSerializer
from apps.shop.models.option import (
    Option,
    OptionItem,
)


class OptionSerializer(ModelMixinSerializer):
    class Meta:
        model = Option
        fields = "__all__"


class OptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionItem
        fields = ["id", "item_name"]
