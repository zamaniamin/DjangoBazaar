from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from apps.shop.models.category import Category, CategoryImage
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers.category_serializers import (
    CategorySerializer,
    CategoryImageSerializer,
    CategoryTreeSerializer,
)


@extend_schema_view(
    create=extend_schema(tags=["Category"], summary="Create a new category"),
    retrieve=extend_schema(tags=["Category"], summary="Retrieve a category"),
    list=extend_schema(tags=["Category"], summary="Retrieve a list of categories"),
    update=extend_schema(tags=["Category"], summary="Update a category"),
    destroy=extend_schema(tags=["Category"], summary="Deletes a category"),
    category_tree=extend_schema(
        tags=["Category"],
        summary="Build a hierarchical tree by assigning each category's children to their parent.",
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = DefaultPagination
    http_method_names = ["post", "get", "put", "delete"]

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
        "category_tree": [AllowAny()],
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

    def get_category_tree(self):
        categories = Category.objects.prefetch_related("children").filter(
            parent__isnull=True
        )
        return categories

    @action(detail=False, methods=["get"], url_path="tree")
    def category_tree(self, request):
        # TODO write test for tree
        root_categories = self.get_category_tree()
        serializer = CategoryTreeSerializer(root_categories, many=True)
        return Response({"categories_tree": serializer.data})


@extend_schema_view(
    create=extend_schema(
        tags=["Category Image"],
        summary="Upload an image",
        parameters=[OpenApiParameter("category_pk", str, OpenApiParameter.PATH)],
    ),
    retrieve=extend_schema(
        tags=["Category Image"],
        summary="Get an image",
        parameters=[
            OpenApiParameter("category_pk", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
    list=extend_schema(
        tags=["Category Image"],
        summary="List images",
        parameters=[OpenApiParameter("category_pk", str, OpenApiParameter.PATH)],
    ),
    update=extend_schema(
        tags=["Category Image"],
        summary="Modify an existing image",
        parameters=[
            OpenApiParameter("category_pk", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
    destroy=extend_schema(
        tags=["Category Image"],
        summary="Remove an existing image",
        parameters=[
            OpenApiParameter("category_pk", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
)
class CategoryImageViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryImageSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["post", "get", "put", "delete"]
    ACTION_PERMISSIONS = {"list": [AllowAny()], "retrieve": [AllowAny()]}

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def get_queryset(self):
        return CategoryImage.objects.filter(
            category_id=self.kwargs["category_pk"]
        ).all()

    def perform_create(self, serializer):
        category_id = self.kwargs["category_pk"]
        category = Category.objects.get(id=category_id)

        # Check if an image already exists for this category
        if CategoryImage.objects.filter(category=category).exists():
            raise ValidationError(
                "An image already exists for this category. Please update the existing image."
            )
        serializer.save(category=category)

    def perform_update(self, serializer):
        category_id = self.kwargs["category_pk"]
        category = Category.objects.get(id=category_id)
        serializer.save(category=category)
