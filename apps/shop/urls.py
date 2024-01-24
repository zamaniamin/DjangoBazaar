from rest_framework_nested import routers

from apps.shop.views.product_views.cart_view import CartViewSet, CartItemViewSet
from apps.shop.views.product_views.image_view import ProductImageViewSet
from apps.shop.views.product_views.product_view import ProductViewSet
from apps.shop.views.product_views.variant_view import VariantViewSet

router = routers.DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("variants", VariantViewSet, basename="variant")
router.register("carts", CartViewSet, basename="cart")

products_router = routers.NestedDefaultRouter(router, "products", lookup="product")
products_router.register("images", ProductImageViewSet, basename="product-images")

cart_items_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_items_router.register("items", CartItemViewSet, basename="cart-items")

urlpatterns = router.urls + products_router.urls + cart_items_router.urls
