from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from apps.shop.models.category import Category
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers.category_serializers import (
    CategorySerializer,
)


@extend_schema_view(
    create=extend_schema(tags=["Category"], summary="Create a new category"),
    retrieve=extend_schema(tags=["Category"], summary="Retrieve a category"),
    list=extend_schema(tags=["Category"], summary="Retrieve a list of categories"),
    update=extend_schema(tags=["Category"], summary="Update a category"),
    destroy=extend_schema(tags=["Category"], summary="Deletes a category"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = DefaultPagination
    http_method_names = ["post", "get", "put", "delete"]

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def get_queryset(self):
        return Category.objects.prefetch_related("image").order_by("-created_at")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Check if the category is its own parent only during update
        if "parent" in serializer.validated_data:
            if serializer.validated_data["parent"] == instance:
                raise serializers.ValidationError(
                    {"parent": "A category cannot be a parent of itself."}
                )

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
