from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.shop.views.product_views.image_view import ProductImageViewSet
from apps.shop.views.product_views.product_view import ProductViewSet

app_name = "products"

# Configure and register the viewset with the router.
router = DefaultRouter()
router.register(r"", ProductViewSet, basename="product")

# Organize URL patterns, including the router endpoints and additional image endpoints.
urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:product_id>/images/",
        ProductImageViewSet.as_view({"get": "list", "post": "create"}),
        name="images",
    ),
    path(
        "<int:product_id>/images/<int:pk>/",
        ProductImageViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="image",
    ),
]
