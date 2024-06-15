from rest_framework import viewsets

from apps.shop.models.category import Category
from apps.shop.serializers.category_serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
