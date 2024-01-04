from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from apps.core.services.time_service import DateTime
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

        # --- response ---
        response_body = {
            "product_id": product.id,
            "product_name": product.product_name,
            "description": product.description,
            "status": product.status,
            "options": self.__dict_product_options(product.productoption_set.all()),
            "variants": self.__dict_product_variants(product.productvariant_set.all()),
            "created_at": DateTime.string(product.created_at),
            "updated_at": DateTime.string(product.updated_at),
            "published_at": DateTime.string(product.published_at),
        }
        return Response(response_body, status=status.HTTP_201_CREATED)

    @staticmethod
    def __dict_product_options(options):
        product_options = []
        for option in options:
            items = option.productoptionitem_set.all()

            product_options.append({
                'option_id': option.id,
                'option_name': option.option_name,
                'items': [{'item_id': item.id, 'item_name': item.item_name} for item in items]
            })
        if product_options:
            return product_options
        else:
            return None

    @staticmethod
    def __dict_product_variants(variants):
        product_variants = []
        for variant in variants:
            product_variants.append({
                "variant_id": variant.id,
                "price": variant.price,
                "stock": variant.stock,
                "option1": variant.option1.item_name if variant.option1 else None,
                "option2": variant.option2.item_name if variant.option2 else None,
                "option3": variant.option3.item_name if variant.option3 else None,
                "created_at": DateTime.string(variant.created_at),
                "updated_at": DateTime.string(variant.updated_at)
            })

        if product_variants:
            return product_variants
        return None
