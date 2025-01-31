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


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "children"]  # Add any other fields you want to include

    def get_children(self, obj):
        # Get the children categories for the current category
        children = obj.children.all()
        return CategoryTreeSerializer(children, many=True).data


class CategorySerializer(TimestampedSerializer):
    image = CategoryImageSerializer(read_only=True)
    parents_hierarchy = serializers.SerializerMethodField()
    children_hierarchy = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "parents_hierarchy",  # TODO write test
            "children_hierarchy",  # TODO write test
            "image",
            "updated_at",
            "created_at",
        ]

    def get_parents_hierarchy(self, obj):
        return obj.get_parents_hierarchy()

    def get_children_hierarchy(self, obj):
        return obj.get_children_hierarchy()
