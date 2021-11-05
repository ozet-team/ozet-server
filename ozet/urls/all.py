# -*- coding: utf-8 -*-
from django.urls import path, include

from .admin import urlpatterns as admin_urlpatterns
from .api import urlpatterns as api_urlpatterns

urlpatterns = [
    # api
    path('api/', include(api_urlpatterns)),

    # admin
    path('admin/', include(admin_urlpatterns)),
]
