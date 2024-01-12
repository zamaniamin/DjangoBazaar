from rest_framework.routers import DefaultRouter

from apps.shop.views.product_views import ProductViewSet, ProductVariantViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("variants", ProductVariantViewSet, basename="product-variant")

urlpatterns = router.urls
