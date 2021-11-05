# -*- coding: utf-8 -*-
import hashlib

import sentry_sdk
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from firebase_admin import auth as firebase_auth
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework_jwt.authentication import (
    JSONWebTokenAuthentication as BaseJSONWebTokenAuthentication,
)


class AuthenticationTokenError(exceptions.AuthenticationFailed):
    default_detail = _('Authentication Token Error')
    default_code = 'authentication_token_error'


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):

    def authenticate(self, request):
        try:
            rv = super(JSONWebTokenAuthentication, self).authenticate(request)
        except exceptions.AuthenticationFailed:
            return

        try:
            user, jwt_value = rv
        except (TypeError, ValueError):
            return rv
        if not user.is_valid_token(jwt_value.decode('utf-8')):
            raise exceptions.AuthenticationFailed()
        request.jwt_value = jwt_value
        return rv


class FirebaseIdTokenSoftAuthentication(BaseAuthentication):
    header_prefix = 'FIT'

    check_revoked = False

    @classmethod
    def remove_payload_cache(cls, user_id, id_token=None):
        keys = []
        if id_token is None:
            pattern = f'fits:{user_id}:*'
            keys.extend(cache.keys(pattern))
        else:
            # noinspection PyBroadException
            try:
                ctx = hashlib.sha256()
                ctx.update(id_token)
                ctx = ctx.hexdigest()
                keys.append(f'fits:{user_id}:{ctx}')
            except Exception:
                return
        for key in keys:
            cache.delete(key)

    def get_id_token(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = self.header_prefix.lower()

        if not auth:
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def get_payload(self, id_token, retry=0):
        try:
            return firebase_auth.verify_id_token(id_token, check_revoked=self.check_revoked)
        except firebase_auth.ExpiredIdTokenError:
            msg = _('Signature has expired.')
            raise AuthenticationTokenError(msg)
        except firebase_auth.RevokedIdTokenError:
            msg = _('Signature has revoked.')
            raise AuthenticationTokenError(msg)
        except firebase_auth.InvalidIdTokenError:
            raise AuthenticationTokenError()
        except firebase_auth.CertificateFetchError:
            if retry < 3:
                return self.get_payload(id_token, retry=retry + 1)
            raise exceptions.APIException()
        except Exception:
            raise exceptions.APIException()

    def authenticate(self, request):
        id_token = self.get_id_token(request)
        if id_token is None:
            return None

        ctx = hashlib.sha256()
        ctx.update(id_token)
        ctx = ctx.hexdigest()

        user_id = None
        # noinspection PyBroadException
        try:
            # noinspection PyProtectedMember
            client = firebase_auth._get_client(app=None)
            # noinspection PyProtectedMember
            header, unverified_payload = client._token_verifier.id_token_verifier._decode_unverified(id_token)
            user_id = unverified_payload.get('user_id', unverified_payload.get('uid'))
        except Exception:
            sentry_sdk.capture_exception()

        if user_id:
            key = f'fits:{user_id}:{ctx}'
            payload = cache.get(key)
            if payload:
                user = self.authenticate_credentials(payload)
                return user, id_token

        payload = self.get_payload(id_token)
        user = self.authenticate_credentials(payload)
        key = f'fits:{user.id}:{ctx}'
        cache.set(key, payload, 3600)
        return user, id_token

    # noinspection PyMethodMayBeStatic
    def authenticate_credentials(self, payload):
        user_cls = get_user_model()
        user_id = int(payload.get('uid'))
        if not user_id:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = user_cls.objects.get(id=user_id)
        except user_cls.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user


class FirebaseIdTokenHardAuthentication(FirebaseIdTokenSoftAuthentication):
    check_revoked = True
