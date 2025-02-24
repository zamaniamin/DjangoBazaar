from django.db import IntegrityError
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.shop.models.cart import Cart, CartItem
from apps.shop.serializers.cart_serializers import (
    CartSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
    CartItemSerializer,
)


@extend_schema_view(
    create=extend_schema(
        tags=["Cart Item"],
        summary="Add one variant to cart",
        parameters=[OpenApiParameter("cart_pk", str, OpenApiParameter.PATH)],
    ),
    retrieve=extend_schema(
        tags=["Cart Item"],
        summary="Retrieve an item from the cart",
        parameters=[
            OpenApiParameter("cart_pk", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
    list=extend_schema(
        tags=["Cart Item"],
        summary="Retrieve a list of items from the cart",
        parameters=[OpenApiParameter("cart_pk", str, OpenApiParameter.PATH)],
    ),
    partial_update=extend_schema(
        tags=["Cart Item"],
        summary="Update an item from the cart",
        parameters=[
            OpenApiParameter("cart_pk", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
    destroy=extend_schema(
        tags=["Cart Item"],
        summary="Deletes an item from the cart",
        parameters=[
            OpenApiParameter("cart_pk", str, OpenApiParameter.PATH),
            OpenApiParameter("id", str, OpenApiParameter.PATH),
        ],
    ),
)
class CartItemViewSet(ModelViewSet):
    http_method_names = ["post", "get", "patch", "delete"]

    def get_queryset(self):
        cart_pk = self.kwargs.get("cart_pk")
        return CartItem.objects.select_related("variant").filter(cart_id=cart_pk).all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def create(self, request, *args, **kwargs):
        # validate data
        cart_id = self.kwargs.get("cart_pk")
        serializer = self.get_serializer(
            data=request.data, context={"cart_pk": cart_id}
        )
        serializer.is_valid(raise_exception=True)

        # get validated data
        payload = serializer.validated_data
        variant = payload["variant"]
        quantity = payload["quantity"]

        try:
            cart_item = CartItem.objects.create(
                cart_id=cart_id, variant_id=variant.id, quantity=quantity
            )
        except IntegrityError:
            return Response(
                {"detail": "This variant already exist in the cart."},
                status=status.HTTP_400_BAD_REQUEST,  # todo change status code to 409
            )

        # return response
        response_serializer = CartItemSerializer(cart_item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    create=extend_schema(tags=["Cart"], summary="Create a new cart"),
    retrieve=extend_schema(tags=["Cart"], summary="Retrieve a cart"),
    list=extend_schema(tags=["Cart"], summary="Retrieve a list of carts"),
    destroy=extend_schema(tags=["Cart"], summary="Deletes a cart"),
)
class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related("items__variant").all()
    http_method_names = ["post", "get", "delete"]

    ACTION_PERMISSIONS = {
        "list": [IsAdminUser()],
    }

    def get_permissions(self):
        return self.ACTION_PERMISSIONS.get(self.action, super().get_permissions())


# TODO check the stock of items before save the order
