from django.urls import re_path
from rest_framework_simplejwt import views

urlpatterns = [
    re_path(r"^create/?", views.TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^refresh/?", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^verify/?", views.TokenVerifyView.as_view(), name="jwt-verify"),
]
