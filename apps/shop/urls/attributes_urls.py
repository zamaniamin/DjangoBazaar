from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.shop.views.attribute_views.attribute_view import (
    AttributeItemViewSet,
    AttributeViewSet,
)

app_name = "attributes"

# Configure and register the viewset with the router.
router = DefaultRouter()
router.register(r"", AttributeViewSet, basename="attribute")
urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:attribute_id>/items/",
        AttributeItemViewSet.as_view({"get": "list", "post": "create"}),
        name="items",
    ),
    path(
        "<int:attribute_id>/items/<int:pk>/",
        AttributeItemViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="item",
    ),
]
