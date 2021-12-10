from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework_jwt.authentication import (
    JSONWebTokenAuthentication as BaseJSONWebTokenAuthentication,
)


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
