from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny

from apps.shop.models import Product, ProductOption
from apps.shop.serializers.product_serializers import ProductOptionSerializer


@extend_schema_view(
    create=extend_schema(
        tags=["Product Option"], summary="Create a new product option"
    ),
    retrieve=extend_schema(
        tags=["Product Option"], summary="Retrieves a single product option"
    ),
    list=extend_schema(
        tags=["Product Option"],
        summary="Retrieves a list of product options",
        # parameters=[
        #     OpenApiParameter(
        #         name="option_name",
        #         description="Filter product options by name",
        #         required=False,
        #         type=str,
        #     )
        # ],
    ),
    update=extend_schema(
        tags=["Product Option"], summary="Updates an existing product option"
    ),
    destroy=extend_schema(
        tags=["Product Option"], summary="Remove an existing product option"
    ),
)
class ProductOptionViewSet(viewsets.ModelViewSet):
    serializer_class = ProductOptionSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["post", "get", "put", "delete"]

    ACTION_PERMISSIONS = {
        "list": [AllowAny()],
        "retrieve": [AllowAny()],
    }

    def get_queryset(self):
        product_id = self.kwargs.get("product_pk")
        get_object_or_404(Product, pk=product_id)
        return ProductOption.objects.filter(product_id=product_id)

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())

    # def create(self, request, *args, **kwargs):
    #     # validate data
    #     option_id = kwargs["option_pk"]
    #     serializer = self.get_serializer(
    #         data=request.data, context={"option_pk": option_id}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #
    #     # check option is exist or not
    #     # TODO can I remove this line?
    #     get_object_or_404(Option, pk=option_id)
    #
    #     # get validated data
    #     payload = serializer.validated_data
    #     item_name = payload["item_name"]
    #
    #     try:
    #         option_item = OptionItem.objects.create(
    #             option_id=option_id, item_name=item_name
    #         )
    #     except IntegrityError:
    #         return Response(
    #             {"item_name": "item with this item name already exists."},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )
    #
    #     # return response
    #     response_serializer = OptionItemSerializer(option_item)
    #     return Response(response_serializer.data, status=status.HTTP_201_CREATED)
