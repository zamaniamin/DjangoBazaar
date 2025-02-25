"""
Django authentication provides both authentication and authorization together and
is generally referred to as the authentication system, as these features are somewhat coupled.

Using the Django authentication system, see:
https://docs.djangoproject.com/en/5.1/topics/auth/default/

Customizing authentication in Django, see:
https://docs.djangoproject.com/en/5.1/topics/auth/customizing/

How to use sessions, see:
https://docs.djangoproject.com/en/5.1/topics/http/sessions/

Settings for Django sessions, see:
https://docs.djangoproject.com/en/5.1/ref/settings/#sessions
"""

from django.urls import re_path
from rest_framework_simplejwt import views

urlpatterns = [
    re_path(r"^create/?", views.TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^refresh/?", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^verify/?", views.TokenVerifyView.as_view(), name="jwt-verify"),
]
