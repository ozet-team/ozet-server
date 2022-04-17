from django.utils.functional import cached_property
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class ClientIPContextMixin(APIView):

    @cached_property
    def client_ip(self):
        if not hasattr(self, 'request') or not self.request:
            return None
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def initialize_request(self, request, *args, **kwargs):
        request = super(ClientIPContextMixin, self).initialize_request(request, *args, **kwargs)
        request.client_ip = self.client_ip
        return request

    def get_serializer_context(self):
        if not hasattr(super(ClientIPContextMixin, self), 'get_serializer_context'):
            return

        # noinspection PyUnresolvedReferences
        context = super(ClientIPContextMixin, self).get_serializer_context()
        if isinstance(self.request, Request):
            context['client_ip'] = self.client_ip
        return context


class ClientVersionContextMixin(APIView):

    @cached_property
    def client_os(self):
        if not hasattr(self, 'request') or not self.request:
            return None
        version = self.request.META.get('HTTP_X_CHATIE_VERSION', '')
        index = version.find('/')
        os, version = version[:index], version[index + 1:]
        return os

    @cached_property
    def client_app_version(self):
        if not hasattr(self, 'request') or not self.request:
            return None
        version = self.request.META.get('HTTP_X_CHATIE_VERSION', '')
        index = version.find('/')
        os, version = version[:index], version[index + 1:]
        return version

    def initialize_request(self, request, *args, **kwargs):
        request = super(ClientVersionContextMixin, self).initialize_request(request, *args, **kwargs)
        request.client_os = self.client_os
        request.client_app_version = self.client_app_version
        return request

    def get_serializer_context(self):
        if not hasattr(super(ClientVersionContextMixin, self), 'get_serializer_context'):
            return

        # noinspection PyUnresolvedReferences
        context = super(ClientVersionContextMixin, self).get_serializer_context()
        if isinstance(self.request, Request):
            context['client_os'] = self.client_os
            context['client_app_version'] = self.client_app_version
        return context


class UserContextMixin(APIView):

    @cached_property
    def user(self):
        if getattr(self, 'swagger_fake_view', False):
            return None

        if hasattr(self.request, 'user'):
            user = self.request.user
            if user.is_authenticated:
                return user
        return None

    def get_serializer_context(self):
        if not hasattr(super(UserContextMixin, self), 'get_serializer_context'):
            return

        # noinspection PyUnresolvedReferences
        context = super(UserContextMixin, self).get_serializer_context()
        if isinstance(self.request, Request):
            context['user'] = self.user

        return context


class QuerySerializerMixin(object):
    query_serializer_class = None

    def get_query_serializer_class(self):
        assert self.query_serializer_class is not None, (
            "'%s' should either include a `query_serializer_class` attribute, "
            "or override the `get_query_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.query_serializer_class

    def get_query_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_query_serializer(self, *args, **kwargs):
        serializer_class = self.get_query_serializer_class()
        kwargs['context'] = self.get_query_serializer_context()

        return serializer_class(*args, **kwargs)

    def validate_query_params(self):
        serializer = self.get_query_serializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data
