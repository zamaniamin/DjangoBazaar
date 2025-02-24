from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.shop.views.category_views.category_view import (
    CategoryViewSet,
    CategoryImageViewSet,
)

app_name = "categories"

# Configure and register the viewset with the router.
router = DefaultRouter()
router.register(r"", CategoryViewSet, basename="category")

# Organize URL patterns, including the router endpoints and additional image endpoints.
urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:category_pk>/images/",
        CategoryImageViewSet.as_view({"get": "list", "post": "create"}),
        name="images",
    ),
]
