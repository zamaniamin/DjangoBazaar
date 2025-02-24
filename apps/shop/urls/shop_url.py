from django.urls import include, path

urlpatterns = [
    path("options/", include("apps.shop.urls.options_urls")),
    path("categories/", include("apps.shop.urls.categories_urls")),
    path("attributes/", include("apps.shop.urls.attributes_urls")),
    path("products/", include("apps.shop.urls.products_urls")),
    path("variants/", include("apps.shop.urls.variants_urls")),
    path("carts/", include("apps.shop.urls.carts_urls")),
]
