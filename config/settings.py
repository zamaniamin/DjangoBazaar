"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Application definition

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # External Packages
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    "debug_toolbar",
    "corsheaders",
    # Made by me
    "apps.core",
    "apps.shop",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Site Framework
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = env.str("STATIC_URL", default="static/")
STATIC_ROOT = os.path.join(env.str("STATIC_ROOT", default=BASE_DIR), "static")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------
# --- Custom User Model ---
# -------------------------

AUTH_USER_MODEL = "core.User"

# ----------------------
# --- Site Framework ---
# ----------------------

SITE_ID = 1

# ----------------------
# --- Email Settings ---
# ----------------------

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env.str("EMAIL_HOST", "smtp.example.com")
    EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", True)
    EMAIL_PORT = env.int("EMAIL_PORT", 0)
    EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", "no-reply@example.com")
    EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", "<password>")

# -------------------------
# --- REST-API Settings ---
# -------------------------

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # "PAGE_SIZE": 10,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Django Bazaar",
    "DESCRIPTION": """An open-source e-commerce platform, offering a versatile and scalable solution for creating 
    online marketplaces. """,
    "VERSION": "0.3.64",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,  # file upload representation in Swagger UI
    # UPLOADED_FILES_USE_URL
}

# --------------------
# --- JWT Settings ---
# --------------------

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("JWT",),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "UPDATE_LAST_LOGIN": True,
}

# --------------------
# --- OTP Settings ---
# --------------------

OTP_SECRET_KEY = env.str("OTP_SECRET_KEY")
OTP_EXPIRE_SECONDS = env.int("OTP_EXPIRE_SECONDS", 360)

# ----------------------
# --- Django Testing ---
# ----------------------

# faster hashing algorithm, reduce tests time.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ----------------------------
# --- Django Debug Toolbar ---
# ----------------------------

# Debug Toolbar is displayed if our IP address is listed in INTERNAL_IPS, in our case, only if we are in DEBUG mode
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

# -------------
# --- Redis ---
# -------------

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env.str("REDIS_URL", "redis://localhost:6379/"),
        "TIMEOUT": 60 * 15,  # in seconds: 60 * 15 (15 minutes)
        # "TIMEOUT": None,  # cache keys never expire, the default value is 5 minutes (300 seconds)
        # "TIMEOUT": 0,  # expire the cache immediately (don’t cache)
    }
}

# -------------
# --- Media ---
# -------------

MEDIA_URL = env.str("MEDIA_URL", default="media/")
MEDIA_ROOT = os.path.join(env.str("MEDIA_ROOT", default=BASE_DIR), "media")

# ------------
# --- ASGI ---
# ------------

ASGI_APPLICATION = "config.asgi.application"

# ------------
# --- CORS ---
# ------------

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:3000",
    ],
)
