from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import api_view

from apps.shop.filters.product_filter import ProductFilter
from apps.shop.paginations import DefaultPagination
from apps.shop.serializers import product_serializers
from apps.shop.services.product_service import ProductService
from apps.shop.models.product import Product
from django.db.models import Q


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
    search_fields = ["name", "description", "category__name", "attribute__name"]
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
        # Validate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        # Create product
        product = ProductService.create_product(**payload)

        # Return the serialized response
        return Response(
            serializer.to_representation(product), status=status.HTTP_201_CREATED
        )

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

    @api_view(['GET'])
    def get_product_item_queryset(request):
        query = request.GET.get('q', '')
        if query:
            products = Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(option_items__item_name__icontains=query)
            ).distinct()
        else:
            products = Product.objects.all()

        serializer = product_serializers.ProductSerializer(products, many=True)
        return Response(serializer.data)

    def get_item_category_queryset(self):
        queryset = Product.objects.all()
        item_name = self.request.query_params.get('item_name', None)

        if item_name:
            queryset = queryset.filter(option_items__item_name__icontains=item_name).select_related('category').distinct()

        return queryset

    def get_product_category_queryset(self):
        queryset = Product.objects.all()
        name = self.request.query_params.get('name', None)
        description = self.request.query_params.get('description', None)
        if name:
            queryset = queryset.filter(name__icontains=name).filter(description__icontains=description).select_related('category').distinct()
        return queryset

# TODO add new variant to product and update the product options base on new items in the variant
