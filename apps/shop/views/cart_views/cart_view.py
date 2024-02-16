from drf_spectacular.utils import extend_schema_view, extend_schema
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
    create=extend_schema(tags=["Cart Item"], summary="Add one variant to cart"),
    retrieve=extend_schema(
        tags=["Cart Item"], summary="Retrieve an item from the cart"
    ),
    list=extend_schema(
        tags=["Cart Item"], summary="Retrieve a list of items from the cart"
    ),
    partial_update=extend_schema(
        tags=["Cart Item"], summary="Update an item from the cart"
    ),
    destroy=extend_schema(tags=["Cart Item"], summary="Deletes an item from the cart"),
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

    def get_serializer_context(self):
        return {"cart_pk": self.kwargs["cart_pk"]}

    def create(self, request, *args, **kwargs):

        # Validate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        cart_id = kwargs["cart_pk"]
        variant = payload["variant"]
        quantity = payload["quantity"]

        try:
            # TODO dont add product with 0 stock
            cart_item = CartItem.objects.get(cart_id=cart_id, variant_id=variant.id)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **payload)

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

# TODO write tests
# TODO show product image
# TODO add cart factory
# TODO check cart queries
# TODO on delete a cart, delete all items from it too
# TODO mange inventory when adding product to cart and when on checkout
# TODO fix 500 error for UUID
# TODO check the stock of items before save the order
# TODO add cart to faker
