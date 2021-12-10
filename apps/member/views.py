from django.utils.functional import cached_property

from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.member import models
from apps.member import serializers
from utils.django.rest_framework.mixins import UserContextMixin


class UserPasscodeVerifyRequestView(CreateAPIView):
    permission_classes = ()
    serializer_class = serializers.UserPasscodeVerifyRequestSerializer

    def post(self, request, *args, **kwargs):
        return super(UserPasscodeVerifyRequestView, self).post(request, *args, **kwargs)


class UserPasscodeVerifyView(CreateAPIView):
    permission_classes = ()
    serializer_class = serializers.UserPasscodeVerifySerializer

    def post(self, request, *args, **kwargs):
        return super(UserPasscodeVerifyView, self).post(request, *args, **kwargs)


class UserMeView(UserContextMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.UserMeSerializer

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != 'put']
        super(UserMeView, self).__init__(*args, **kwargs)

    @cached_property
    def get_object(self):
        if getattr(self, 'swagger_fake_view', False):
            return None

        return self.user

    def get(self, request, *args, **kwargs):
        return super(UserMeView, self).get(request, *args, **kwargs)
