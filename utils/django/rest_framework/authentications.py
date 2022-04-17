from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request
from rest_framework_jwt.authentication import (
    JSONWebTokenAuthentication as BaseJSONWebTokenAuthentication,
)


class SwaggerTokenAuthentication(BaseAuthentication):
    api_key_name = "HTTP_OZET_SWAGGER_API_KEY"
    auth_key = "ozetozet"

    def authenticate(self, request):
        if not settings.DEBUG:
            return None

        if swagger_api_key := request.META.get(self.api_key_name, ""):
            if swagger_api_key == self.auth_key:
                anonymous_user = AnonymousUser
                anonymous_user.is_authenticated = lambda: True
                return (anonymous_user, None)

        return None


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):
    def authenticate(self, request: Request):
        try:
            rv = super(JSONWebTokenAuthentication, self).authenticate(request)
        except exceptions.AuthenticationFailed:
            return

        try:
            user, jwt_value = rv
        except (TypeError, ValueError):
            return rv

        if not user.is_valid_token(jwt_value.decode("utf-8")):
            raise exceptions.AuthenticationFailed()

        request.jwt_value = jwt_value

        return rv
