from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from apps.shop.models import Product, ProductVariant
from apps.shop.serializers import product_serializers as s
from apps.shop.services.product_service import ProductService


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = s.ProductSerializer
    permission_classes = [IsAdminUser]

    ACTION_SERIALIZERS = {
        'create': s.ProductCreateSerializer,
    }

    ACTION_PERMISSIONS = {
        'list': [AllowAny()],
        'retrieve': [AllowAny()]
    }

    def get_serializer_class(self):
        return self.ACTION_SERIALIZERS.get(self.action, self.serializer_class)

    def get_permissions(self):
        #  If the action is not in the dictionary, it falls back to the default permission class/.
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    def get_queryset(self):
        """
        Get the queryset for the Product model with related options and variants.

        Returns:
            QuerySet: A queryset for the Product model with select and prefetch related options and variants.
        """

        return Product.objects.select_related().prefetch_related(
            'productoption_set__productoptionitem_set',
            Prefetch(
                'productvariant_set',
                queryset=ProductVariant.objects.select_related('option1', 'option2', 'option3')))

    def create(self, request, *args, **kwargs):
        # --- validate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        # --- create product ---
        product = ProductService.create_product(**payload)

        # Serialize the created product for the response
        response_serializer = s.ProductSerializer(product)

        # Return the serialized response
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
