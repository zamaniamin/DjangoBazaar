from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.core.services.time_service import DateTime
from apps.shop.models import Product
from apps.shop.serializers import product_serializers as s
from apps.shop.services.product_service import ProductService


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = s.ProductSerializer
    permission_classes = [IsAdminUser]

    ACTION_SERIALIZERS = {
        'create': s.ProductCreateSerializer,
    }

    def get_serializer_class(self):
        return self.ACTION_SERIALIZERS.get(self.action, self.serializer_class)

    def create(self, request, *args, **kwargs):
        # --- validate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        # --- create product ---
        product, options, variants = ProductService.create_product(**payload)

        # --- response ---
        response_body = {
            "product_id": product.id,
            "product_name": product.product_name,
            "description": product.description,
            "status": product.status,
            "options": options,
            "variants": variants,
            "created_at": DateTime.string(product.created_at),
            "updated_at": DateTime.string(product.updated_at),
            "published_at": DateTime.string(product.published_at),
        }
        return Response(response_body, status=status.HTTP_201_CREATED)
