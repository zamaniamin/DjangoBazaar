from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from apps.shop.models import Product
from apps.shop.serializers import product_serializer as s


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = s.ProductSerializer
    permission_classes = [IsAdminUser]
