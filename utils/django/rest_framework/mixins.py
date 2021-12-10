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
