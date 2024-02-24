from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import mixins
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.viewsets import GenericViewSet

from apps.shop.models import ProductVariant
from apps.shop.serializers import product_serializers


@extend_schema_view(
    retrieve=extend_schema(
        tags=["Product Variant"], summary="Retrieves a single product variant"
    ),
    update=extend_schema(
        tags=["Product Variant"], summary="Updates an existing product variant"
    ),
    partial_update=extend_schema(
        tags=["Product Variant"], summary="Partial updates an existing product variant"
    ),
    destroy=extend_schema(
        tags=["Product Variant"], summary="Remove an existing product variant"
    ),
)
class VariantViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = ProductVariant.objects.all()
    serializer_class = product_serializers.ProductVariantSerializer
    permission_classes = [IsAdminUser]

    ACTION_PERMISSIONS = {"retrieve": [AllowAny()]}

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())
