from rest_framework import serializers

from apps.core.serializers.timestamped_serializer import TimestampedSerializer
from apps.shop.models.category import Category, CategoryImage


class CategoryImageSerializer(TimestampedSerializer):
    category_id = serializers.IntegerField(source="category.id", read_only=True)
    src = serializers.ImageField(required=True)
    alt = serializers.CharField(required=False, allow_null=True, default=None)

    class Meta:
        model = CategoryImage
        fields = ["id", "category_id", "src", "alt", "updated_at", "created_at"]


class CategorySerializer(TimestampedSerializer):
    image = CategoryImageSerializer(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "image",
            "updated_at",
            "created_at",
        ]
