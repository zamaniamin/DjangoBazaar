from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.permissions import IsAdminUser
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


# TODO fix 500 error for UUID
# TODO show product image
# TODO mange inventory when adding product to cart and when on checkout
# TODO deactivate PUT and PATCH for cart
# TODO add cart factory
# TODO write tests
# TODO on delete a cart, delete all items from it too
# TODO check the stock of items before save the order
