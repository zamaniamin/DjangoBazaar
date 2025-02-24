from django.urls import include, path

urlpatterns = [
    path("products/", include("apps.shop.urls.product_url")),
    path("variants/", include("apps.shop.urls.variants_urls")),
    path("carts/", include("apps.shop.urls.carts_urls")),
]
