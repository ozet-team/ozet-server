# -*- coding: utf-8 -*-
from django.urls import path, include

from .apis.auth import urls as auth_urls

urlpatterns = [
    # Auth
    path('', include(auth_urls)),
]
