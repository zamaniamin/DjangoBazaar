from rest_framework_nested import routers

from apps.shop.views.product_views.image_view import ProductImageViewSet
from apps.shop.views.product_views.product_view import ProductViewSet
from apps.shop.views.product_views.variant_view import VariantViewSet

router = routers.DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("variants", VariantViewSet, basename="variant")

products_router = routers.NestedDefaultRouter(router, "products", lookup="product")
products_router.register("images", ProductImageViewSet, basename="product-images")

urlpatterns = router.urls + products_router.urls
