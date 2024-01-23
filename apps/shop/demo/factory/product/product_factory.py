from factory.django import DjangoModelFactory

from apps.shop.models import Product


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
