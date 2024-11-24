from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from apps.shop.models import Product, ProductOption
from apps.shop.serializers.product_serializers import ProductOptionSerializer
from apps.shop.services.product_service import ProductOptionService


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

    def create(self, request, *args, **kwargs):
        # validate data
        product_id = kwargs["product_pk"]
        serializer = self.get_serializer(
            data=request.data, context={"product_pk": product_id}
        )
        serializer.is_valid(raise_exception=True)

        # check product is existed or not
        product = get_object_or_404(Product, pk=product_id)

        # get validated data
        payload = serializer.validated_data
        option_name = payload["option_name"]
        items = payload["items"]

        try:
            ProductOptionService.create_option(product, option_name, items)
        except ValidationError as e:
            if e.code == "max_options_exceeded":
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # return response: fetch the updated list of options after creation
        product_options = ProductOption.objects.filter(product_id=product_id)
        response_serializer = ProductOptionSerializer(product_options, many=True)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
