from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.member import models
from apps.member import serializers


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


