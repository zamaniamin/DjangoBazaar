from django.urls import re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views

from apps.core.views.users.user_management_views import UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = router.urls

urlpatterns += [
    re_path(r"^jwt/create/?", views.TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^jwt/refresh/?", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^jwt/verify/?", views.TokenVerifyView.as_view(), name="jwt-verify"),
]
