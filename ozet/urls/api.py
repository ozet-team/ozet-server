"""chatie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
import json
import re

from django.conf.urls import url
from django.core import exceptions as django_exceptions
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.views import APIView

from utils.django.rest_framework.request import get_ip
from utils.internal_auth import create_internal_auth_urls, internal_auth_required


def _has_perm(request, allowed=None):
    ip = get_ip(request)
    if ip in ('127.0.0.1', 'localhost'):
        return True

    if not allowed:
        return False

    return ip in allowed


def handle_error(request, exc):

    class ErrorView(APIView):
        permission_classes = []

        def get(self, *args, **kwargs):
            raise exc

        def post(self, *args, **kwargs):
            raise exc

        def put(self, *args, **kwargs):
            raise exc

        def patch(self, *args, **kwargs):
            raise exc

        def delete(self, *args, **kwargs):
            raise exc

    return ErrorView.as_view()(request)


def handle_400(request, exception=None):
    exception = exception or django_exceptions.SuspiciousOperation()
    return handle_error(request, exception)


def handle_403(request, exception=None):
    exception = exception or django_exceptions.PermissionDenied()
    return handle_error(request, exception)


def handle_404(request, exception=None):
    exception = exception or Http404()
    return handle_error(request, exception)


def handle_500(request, exception=None):
    exception = exception or HttpResponseServerError()
    return handle_error(request, exception)


def liveness(request):
    return HttpResponse('ok')


def readiness(request):
    return HttpResponse('ok')


def headers(request):
    from django.conf import settings

    allowed = getattr(settings, 'OFFICE_IPS', [])
    if not _has_perm(request, allowed):
        HttpResponse(json.dumps({}), content_type="application/json")

    regex = re.compile('^HTTP_')
    _headers = dict((regex.sub('', header), value)
                    for (header, value) in request.META.items() if header.startswith('HTTP_'))
    return HttpResponse(json.dumps(_headers), content_type="application/json")


# Handlers
handler400 = f'{__name__}.handle_400'
handler403 = f'{__name__}.handle_403'
handler404 = f'{__name__}.handle_404'
handler500 = f'{__name__}.handle_500'

# Internal Auth
internal_auth_urls = create_internal_auth_urls()


# Docs
schema_view = get_schema_view(
   openapi.Info(
      title="채티 API",
      default_version='v1',
      contact=openapi.Contact(email='devteam@eineblu.me'),
      license=openapi.License(name="Copyright © EINEBLUME CO., LTD. 2018-2019 All Rights Reserved"),
   ),
   url=swagger_settings.DEFAULT_API_URL,
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Internal Auth
    path('', include(internal_auth_urls)),

    # APIs
    path('', include(('user.urls', 'user'))),

    # Docs
    url(r'^docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='docs-schema'),
    url(r'^docs/$', internal_auth_required(schema_view.with_ui('swagger', cache_timeout=0)), name='docs'),

    # Health Check
    path('liveness/', liveness),
    path('readiness/', readiness),

    # Etc
    path('headers/', headers),
]
