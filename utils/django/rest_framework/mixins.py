from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class UserContextMixin(APIView):
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
