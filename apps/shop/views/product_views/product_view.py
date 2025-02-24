from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from apps.shop.filters.product_filter import ProductFilter
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers import product_serializers
from apps.shop.services.product.product_service import ProductService


@extend_schema_view(
    create=extend_schema(tags=["Product"], summary="Create a new product"),
    retrieve=extend_schema(tags=["Product"], summary="Retrieve a single product."),
    list=extend_schema(tags=["Product"], summary="Retrieve a list of products"),
    update=extend_schema(tags=["Product"], summary="Update a product"),
    partial_update=extend_schema(tags=["Product"], summary="Partial update a product"),
    destroy=extend_schema(tags=["Product"], summary="Deletes a product"),
    list_variants=extend_schema(
        tags=["Product Variant"], summary="Retrieves a list of product variants"
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = product_serializers.ProductSerializer
    permission_classes = [IsAdminUser]
    # TODO add test case for search, filter, ordering and pagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "description"]
    filterset_class = ProductFilter
    ordering_fields = [
        "name",
        "created_at",
        "update_at",
        "published_at",
        "variants__stock",
        "variants__price",
    ]
    pagination_class = DefaultPagination

    ACTION_SERIALIZERS = {
        "create": product_serializers.ProductCreateSerializer,
        "update": product_serializers.ProductUpdateSerializer,
    }

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
        "list_variants": [AllowAny()],
    }

    def get_serializer_class(self):
        return self.ACTION_SERIALIZERS.get(self.action, self.serializer_class)

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def get_queryset(self):
        return ProductService.get_product_queryset(self.request)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.perform_create(serializer)
        serializer = self.serializer_class(product)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.to_representation(product),
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        product_data = serializer.validated_data
        return ProductService.create_product(**product_data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = self.perform_update(serializer)
        return Response(
            serializer.to_representation(product), status=status.HTTP_200_OK
        )

    def perform_update(self, serializer):
        product_data = serializer.validated_data
        try:
            product = ProductService.update_product(self.get_object(), **product_data)
        except ValidationError as e:
            if e.code == "max_options_exceeded":
                raise serializers.ValidationError({"detail": e.messages[0]})
            raise serializers.ValidationError({"detail": str(e)})
        return product

    # ----------------
    # --- variants ---
    # ----------------

    @action(detail=True, methods=["get"], url_path="variants")
    def list_variants(self, request, pk=None):
        """Retrieve and return a list of variants associated with a specific product."""

        product = self.get_object()
        variants = product.variants.all()
        serializer = product_serializers.ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)


# TODO remove product images after product was removed.
