from rest_framework import serializers

from apps.shop.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Category
        fields = "__all__"

    def validate(self, data):
        # Check if the category is its own parent
        if "parent" in data and data["parent"] == self.instance:
            raise serializers.ValidationError(
                "A category cannot be a parent of itself."
            )
        return data
