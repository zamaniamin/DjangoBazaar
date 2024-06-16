from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, AllowAny

from apps.shop.models.category import Category
from apps.shop.paginations import DefaultPagination
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
    queryset = Category.objects.all().order_by('created_at')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = DefaultPagination

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())
