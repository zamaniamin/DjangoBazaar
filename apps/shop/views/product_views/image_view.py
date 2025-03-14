from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from apps.shop.models.product import ProductImage
from apps.shop.serializers.product_serializers import ProductImageSerializer
from apps.shop.services.product.product_service import ProductService


@extend_schema_view(
    create=extend_schema(
        tags=["Product Image"],
        summary="Create multi product image",
        parameters=[OpenApiParameter("product_id", str, OpenApiParameter.PATH)],
    ),
    retrieve=extend_schema(
        tags=["Product Image"],
        summary="Get a single product image",
        parameters=[
            OpenApiParameter("product_id", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
    list=extend_schema(
        tags=["Product Image"],
        summary="Get all product images",
        parameters=[OpenApiParameter("product_id", str, OpenApiParameter.PATH)],
    ),
    update=extend_schema(
        tags=["Product Image"],
        summary="Modify an existing product image",
        parameters=[
            OpenApiParameter("product_id", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
    partial_update=extend_schema(
        tags=["Product Image"],
        summary="Partial update an existing product image",
        parameters=[
            OpenApiParameter("product_id", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
    destroy=extend_schema(
        tags=["Product Image"],
        summary="Remove an existing Product Image",
        parameters=[
            OpenApiParameter("product_id", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
)
class ProductImageViewSet(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    ACTION_PERMISSIONS = {"list": [AllowAny()], "retrieve": [AllowAny()]}

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return ProductImage.objects.filter(product_id=product_id)

    def create(self, request, *args, **kwargs):
        """Upload images for a specific product."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        images = self.perform_create(serializer)
        serializer = self.serializer_class(images, many=True)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        product_id = self.kwargs.get("product_id")
        images_data = serializer.validated_data
        return ProductService.upload_product_images(product_id, **images_data)
