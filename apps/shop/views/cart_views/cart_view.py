import uuid

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.shop.models import Product
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
        cart_pk = self.kwargs["cart_pk"]
        return CartItem.objects.select_related("variant").filter(cart_id=cart_pk).all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def create(self, request, *args, **kwargs):
        # Validate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        cart_id = kwargs["cart_pk"]
        variant = payload["variant"]
        quantity = payload["quantity"]

        # validate `cart_pk`
        try:
            uuid.UUID(cart_id, version=4)
        except ValueError:
            raise ValidationError("Invalid cart_pk. It must be a valid UUID4.")

        get_object_or_404(Cart, pk=cart_id)

        # save cart item
        product = Product.objects.get(id=variant.product_id)
        if product.status != Product.STATUS_ACTIVE:
            raise ValidationError(
                "Inactive products cannot be added to the cart. Please choose an active product."
            )

        # TODO check the variant stock is not 0
        # TODO dont add variant with 0 stock

        cart_item, created = CartItem.objects.get_or_create(
            cart_id=cart_id, variant_id=variant.id, defaults={"quantity": quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

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

# TODO show product image
# TODO write tests
# TODO add cart factory
# TODO add cart to faker
# TODO check cart queries
# TODO on delete a cart, delete all items from it too
# TODO mange inventory when adding product to cart and when on checkout
# TODO fix 500 error for UUID
# TODO check the stock of items before save the order
