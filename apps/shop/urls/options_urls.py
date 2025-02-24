from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.shop.views.option_views.option_view import OptionItemViewSet, OptionViewSet

app_name = "options"

# Configure and register the viewset with the router.
router = DefaultRouter()
router.register(r"", OptionViewSet, basename="option")
urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:option_pk>/items/",
        OptionItemViewSet.as_view({"get": "list", "post": "create"}),
        name="items",
    ),
    path(
        "<int:option_pk>/items/<int:pk>/",
        OptionItemViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="item",
    ),
]
