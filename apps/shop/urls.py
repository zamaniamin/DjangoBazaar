from rest_framework.routers import DefaultRouter

from apps.shop.views.product_views.product_view import ProductViewSet
from apps.shop.views.product_views.variant_view import VariantViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("variants", VariantViewSet, basename="variant")

urlpatterns = router.urls
