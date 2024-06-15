from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets

from apps.shop.models.category import Category
from apps.shop.serializers.category_serializers import CategorySerializer


@extend_schema_view(
    create=extend_schema(tags=["Category"], summary="Create a new category"),
    retrieve=extend_schema(tags=["Category"], summary="Retrieve a category"),
    list=extend_schema(tags=["Category"], summary="Retrieve a list of categories"),
    update=extend_schema(tags=["Category"], summary="Update a category"),
    partial_update=extend_schema(
        tags=["Category"], summary="Partial update a category"
    ),
    destroy=extend_schema(tags=["Category"], summary="Deletes a category"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
