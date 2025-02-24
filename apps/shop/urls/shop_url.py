from django.urls import include, path

urlpatterns = [
    path("products/", include("apps.shop.urls.product_url")),
]
