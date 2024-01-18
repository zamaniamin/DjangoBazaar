from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from apps.shop.models import Product, ProductVariant
from apps.shop.serializers import product_serializers as s
from apps.shop.services.product_service import ProductService


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
    queryset = Product.objects.all()
    serializer_class = s.ProductSerializer
    permission_classes = [IsAdminUser]

    ACTION_SERIALIZERS = {
        "create": s.ProductCreateSerializer,
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
        queryset = Product.objects.select_related().prefetch_related(
            "options__items",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.select_related(
                    "option1", "option2", "option3"
                ),
            ),
            "media",
        )

        user = self.request.user
        if not user.is_staff:
            queryset = queryset.exclude(status="draft")

        return queryset

    def create(self, request, *args, **kwargs):
        # Validate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        # Create product
        product = ProductService.create_product(**payload)

        # Serialize the created product for the response
        response_serializer = s.ProductSerializer(product)

        # Return the serialized response
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # ----------------
    # --- variants ---
    # ----------------

    @action(detail=True, methods=["get"], url_path="variants")
    def list_variants(self, request, pk=None):
        """Retrieve and return a list of variants associated with a specific product."""

        product = self.get_object()
        variants = product.variants.all()
        serializer = s.ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)


# TODO filter products by status, IDs, names, options, price, stock, date,
# TODO add new variant to product and update the product options base on new items in the variant
# @action(detail=True, methods=["post"], url_path="variants")
# def create_variant(self, request, pk=None):
#     """"Creates a new product variant""""
#     ...
