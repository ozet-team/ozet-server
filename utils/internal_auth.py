# -*- coding: utf-8 -*-
from functools import wraps
from urllib.parse import unquote_plus, quote_plus

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, reverse


def _convert_to_https(url: str):
    return url.replace("http://", "https://")


def _get_client():
    return getattr(settings, 'INTERNAL_AUTH', {}).get('client', None)


def _get_session_key():
    return getattr(settings, 'INTERNAL_AUTH', {}).get('token_session_key', 'internal_access_token')


def _get_allowed_domains():
    return getattr(settings, 'INTERNAL_AUTH', {}).get('allowed_domains', [])


def default_handle_authorize(request, _, token, user_info):
    session_key = _get_session_key()
    try:
        del request.session[session_key]
    except KeyError:
        pass

    if not user_info:
        raise PermissionDenied()

    email = user_info.get('email')
    domain = email.split('@')[1]
    allowed_domains = _get_allowed_domains()
    if domain not in allowed_domains:
        raise PermissionDenied()

    request.session[session_key] = token['access_token']
    return redirect(unquote_plus(request.GET.get('state', '/')))


def create_login_endpoint(remote_app, auth_route_name):
    def login(request):
        params = {}
        state = request.GET.get('state', None)
        if state:
            params['state'] = state
        redirect_uri = _convert_to_https(request.build_absolute_uri(reverse(auth_route_name)))
        return remote_app.authorize_redirect(request, redirect_uri, **params)
    return login


def create_auth_endpoint(remote_app, handle_authorize):
    def auth(request):
        token = remote_app.authorize_access_token(request)
        user = remote_app.parse_id_token(request, token)
        return handle_authorize(request, remote_app, token, user)
    return auth


def create_internal_auth_urls(handle_authorize=default_handle_authorize):
    oauth = OAuth()
    client = _get_client()
    remote_app = oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_id=client.get('client_id'),
        client_secret=client.get('client_secret'),
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    login_route_name = 'internal_login'
    auth_route_name = 'internal_callback'
    login = create_login_endpoint(remote_app, auth_route_name)
    auth = create_auth_endpoint(remote_app, handle_authorize)

    return [
        path('internal/login/', login, name=login_route_name),
        path('internal/auth/', auth, name=auth_route_name),
    ]


def internal_auth_required(f):
    @wraps(f)
    def inner(request, *args, **kwargs):
        if getattr(settings, 'DEBUG', False):
            return f(request, *args, **kwargs)

        # TODO : 현재 GCP 셋팅이 안되어 있기 때문에 무조건 진입가능하도록 설정
        return f(request, *args, **kwargs)

        session_key = _get_session_key()
        access_token = request.session.get(session_key, None)
        if access_token:
            return f(request, *args, **kwargs)

        url = _convert_to_https(reverse('internal_login'))
        state = quote_plus(_convert_to_https(request.build_absolute_uri()))
        return HttpResponseRedirect(f'{url}?state={state}')
    return inner
