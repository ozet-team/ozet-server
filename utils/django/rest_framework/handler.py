# -*- coding: utf-8 -*-
import uuid

from calendar import timegm
from datetime import datetime

from django.conf import settings
from django.core import exceptions as django_exceptions
from django.http import Http404
from django.utils.translation import ugettext_lazy

from rest_framework import exceptions as api_exceptions, status
from rest_framework.response import Response
from rest_framework.views import set_rollback
from rest_framework_jwt.compat import get_username_field, get_username
from rest_framework_jwt.settings import api_settings

_IGNORED_ERRORS = set([])


class BadRequest(api_exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = ugettext_lazy('Bad Request')
    default_code = 'bad_request'


def ignore_error(error_cls):
    _IGNORED_ERRORS.add(error_cls)


def jwt_payload_handler(user):
    username_field = get_username_field()
    username = get_username(user)

    payload = {
        'user_id': user.pk,
        'username': username,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)

    payload[username_field] = username

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload


def exception_handler(exc, context):
    # handle api errors
    res = _handle_api_exception(exc, context)
    if res is not None:
        return res

    # handle django errors
    res = _handle_django_exception(exc, context)
    if res is not None:
        return res

    if settings.DEBUG or getattr(settings, 'PY_TEST', False):
        raise exc

    return _handle_api_exception(api_exceptions.APIException(), context)


def _handle_api_exception(exc, context):
    if isinstance(exc, api_exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        data = {
            'code': exc.__class__.__name__,
            'message': None,
            'errors': {},
        }
        if isinstance(exc.detail, (list, tuple)):
            data['message'] = exc.detail[0] if exc.detail else ''
        elif isinstance(exc.detail, dict):
            data['errors'] = exc.detail
        else:
            data['message'] = exc.detail

        set_rollback()
        if status.is_server_error(exc.status_code):
            ignored_errors = tuple(_IGNORED_ERRORS)
            if ignored_errors:
                if not isinstance(exc, ignored_errors):
                    pass
                    #sentry_sdk.capture_exception()
            else:
                pass
                #sentry_sdk.capture_exception()
        return Response(data, status=exc.status_code, headers=headers)
    return None


def _handle_django_exception(exc, context):
    if isinstance(exc, Http404):
        return _handle_api_exception(api_exceptions.NotFound(), context)

    if isinstance(exc, django_exceptions.PermissionDenied):
        return _handle_api_exception(api_exceptions.PermissionDenied(), context)

    if isinstance(exc, django_exceptions.SuspiciousOperation):
        return _handle_api_exception(BadRequest(exc.__class__.__name__), context)

    return None
