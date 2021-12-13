"""
Django settings for ozet project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import datetime

# fmt: off
# flake8: noqa
import os
import sys
from pathlib import Path

import pymysql

pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-#0h9soeou1rahfm#+7@eu1gl1zyv0mz)$u63^q+otr*gtfxl4="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [
        "api.ozet.app",
        "api-staging.ozet.app",
        "hybrid.ozet.app",
        "hybrid-staging.ozet.app",
        "web.ozet.app",
        "web-staging.ozet.app",
        "localhost",
        "127.0.0.1",
    ]

# Application definition

INSTALLED_APPS = [
    "suit",
    #
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #
    "storages",
    #
    "apps.member",
    "apps.resume",
    "apps.announcement",
    #
    "rest_framework",
    'rest_framework.authtoken',
    #
    'rest_auth',
    #
    'corsheaders',
    #
    "django_filters",
    "drf_spectacular",

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ozet.urls"

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

WSGI_APPLICATION = "ozet.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ozet',
        'USER': 'admin',
        'PASSWORD': 'ozetword!',
        'HOST': 'db-staging.ozet.app',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "ko"

TIME_ZONE = "Asia/Seoul"

USE_I18N = False

USE_L10N = True

USE_TZ = False

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

APPEND_SLASH = True
TRIM_SLASH = True

# DRF
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'utils.django.rest_framework.authentications.JSONWebTokenAuthentication',
        'utils.django.rest_framework.authentications.SwaggerTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'commons.contrib.rest_framework.parser.NoUnderscoreBeforeNumberCamelCaseJSONParser',
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
        'drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields',
    ],
}

# Authentication
# https://docs.djangoproject.com/ko/2.1/topics/auth/customizing/#substituting-a-custom-user-model
AUTH_USER_MODEL = 'member.User'

# django-rest-auth
# https://django-rest-auth.readthedocs.io/en/latest/
REST_USE_JWT = True
REST_SESSION_LOGIN = False
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'apps.member.serializers.UserDetailsSerializer',
    'JWT_SERIALIZER': 'apps.member.serializers.JWTSerializer',
}

# django-rest-framework-jwt
# https://getblimp.github.io/django-rest-framework-jwt/
JWT_AUTH = {
    'JWT_PAYLOAD_HANDLER': 'utils.django.rest_framework.handler.jwt_payload_handler',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=15),
}

# django-cors-headers
if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = [
        'http://127.0.0.1:3000',
        'http://localhost:3000'
    ]

CORS_ALLOW_CREDENTIALS = True

# Storage
AWS_ACCESS_KEY_ID = "AKIAWXCSGYGYL3SVFF4G"
AWS_SECRET_ACCESS_KEY = "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"

AWS_REGION = 'ap-northeast-2'
AWS_STORAGE_BUCKET_NAME = 'ozet-bucket'

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

MEDIAFILES_LOCATION = 'media'
STATICFILES_LOCATION = 'static'

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024000000  # value in bytes 1 GB here
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024000000  # value in bytes 1 GB here

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/'
DEFAULT_FILE_STORAGE = 'ozet.storages.S3MediaStorage'

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/'
STATICFILES_STORAGE = 'ozet.storages.S3StaticStorage'

