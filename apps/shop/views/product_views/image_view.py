from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from apps.shop.models import ProductMedia
from apps.shop.serializers import product_serializers as s
from apps.shop.services.product_service import ProductService


@extend_schema_view(
    create=extend_schema(tags=["Product Image"], summary="Create multi product image"),
    retrieve=extend_schema(
        tags=["Product Image"], summary="Get a single product image"
    ),
    list=extend_schema(tags=["Product Image"], summary="Get all product images"),
    update=extend_schema(
        tags=["Product Image"], summary="Modify an existing product image"
    ),
    partial_update=extend_schema(
        tags=["Product Image"], summary="Partial update an existing product image"
    ),
    destroy=extend_schema(
        tags=["Product Image"], summary="Remove an existing Product Image"
    ),
)
class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = s.ProductImageSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    ACTION_PERMISSIONS = {"list": [AllowAny()], "retrieve": [AllowAny()]}

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def get_queryset(self):
        product_pk = self.kwargs["product_pk"]
        return ProductMedia.objects.filter(product_id=product_pk).all()

    def create(self, request, *args, **kwargs):
        """Upload images for a specific product."""

        # validate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        # save images
        product_id = self.kwargs["product_pk"]
        ProductService.create_product_images(product_id, **payload)

        # retrieve all images of current product
        updated_images = ProductMedia.objects.filter(product_id=product_id)
        serializer = s.ProductImageSerializer(updated_images, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
