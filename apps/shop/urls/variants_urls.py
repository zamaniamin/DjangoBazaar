from rest_framework.routers import DefaultRouter

from apps.shop.views.product_views.variant_view import VariantViewSet

app_name = "variants"

# Configure and register the viewset with the router.
router = DefaultRouter()
router.register(r"", VariantViewSet, basename="variant")
urlpatterns = router.urls
