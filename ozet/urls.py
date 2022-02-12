"""ozet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from apps.address import urls as address_urls
from apps.announcement import urls as announcement_urls
from apps.member import urls as member_urls
from apps.resume import urls as resume_urls
from commons.contrib.drf_spectacular import *  # noqa: F403, F401
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", lambda *args, **kwargs: HttpResponse("Hello")),
    path(
        "api/v1/",
        include(
            [
                path("member/", include(member_urls)),
                path("member/", include(resume_urls)),
                path("announcement/", include(announcement_urls)),
                path("address/", include(address_urls)),
            ]
        ),
    ),
]


if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
    )

    debug_urlpatterns = [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "swagger/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
    ]

    urlpatterns += debug_urlpatterns
