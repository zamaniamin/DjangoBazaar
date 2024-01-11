from rest_framework.routers import DefaultRouter

from apps.shop.views.product_views import ProductView

router = DefaultRouter()
router.register("", ProductView,basename="product")

urlpatterns = router.urls
