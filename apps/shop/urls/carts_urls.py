from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.shop.views.cart_views.cart_view import CartViewSet, CartItemViewSet

app_name = "carts"

# Configure and register the viewset with the router.
router = DefaultRouter()
router.register(r"", CartViewSet, basename="cart")
urlpatterns = [
    path("", include(router.urls)),
    path(
        "<uuid:cart_id>/items/",
        CartItemViewSet.as_view({"get": "list", "post": "create"}),
        name="items",
    ),
    path(
        "<uuid:cart_id>/items/<int:pk>/",
        CartItemViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="item",
    ),
]
