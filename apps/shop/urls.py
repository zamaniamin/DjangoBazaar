from rest_framework_nested import routers

from apps.shop.views.attribute_views.attribute_view import (
    AttributeViewSet,
    AttributeItemViewSet,
)
from apps.shop.views.cart_views.cart_view import CartViewSet, CartItemViewSet
from apps.shop.views.category_views.category_view import CategoryViewSet
from apps.shop.views.option_views.option_view import OptionViewSet, OptionItemViewSet
from apps.shop.views.product_views.image_view import ProductImageViewSet
from apps.shop.views.product_views.product_option_view import ProductOptionViewSet
from apps.shop.views.product_views.product_view import ProductViewSet
from apps.shop.views.product_views.variant_view import VariantViewSet

router = routers.DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("variants", VariantViewSet, basename="variant")
router.register("carts", CartViewSet, basename="cart")
router.register("options", OptionViewSet, basename="option")
router.register("categories", CategoryViewSet, basename="category")
router.register("attributes", AttributeViewSet, basename="attribute")

products_router = routers.NestedDefaultRouter(router, "products", lookup="product")
products_router.register("images", ProductImageViewSet, basename="product-images")
products_router.register("options", ProductOptionViewSet, basename="product-options")

cart_items_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_items_router.register("items", CartItemViewSet, basename="cart-items")

option_items_router = routers.NestedDefaultRouter(router, "options", lookup="option")
option_items_router.register("items", OptionItemViewSet, basename="option-items")

attribute_items_router = routers.NestedDefaultRouter(
    router, "attributes", lookup="attribute"
)
attribute_items_router.register(
    "items", AttributeItemViewSet, basename="attribute-items"
)

urlpatterns = (
    router.urls
    + products_router.urls
    + cart_items_router.urls
    + option_items_router.urls
    + attribute_items_router.urls
)
