from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from apps.shop.models import Product
from apps.shop.serializers import product_serializers as s


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
        # todo[] create variants

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        product, options, variants = Product.objects.create_product(**payload)

        response_body = {
            'product_id': product.id,
            'product_name': product.product_name,
            'description': product.description,
            'status': product.status,
            'options': options,
            'variants': variants,
            'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return Response(response_body, status=status.HTTP_201_CREATED)
