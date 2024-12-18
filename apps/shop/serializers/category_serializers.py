from rest_framework import serializers

from apps.shop.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "parent",
            "slug",
            "description",
            "image",
            "created_at",
            "updated_at",
        ]
