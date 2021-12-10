from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from apps.member import models
from apps.member import serializers


class UserPasscodeVertifyRequestView(CreateAPIView):
    permission_classes = ()
    serializer_class = serializers.UserPasscodeVertifySerializer

    def post(self, request, *args, **kwargs):
        """
        @TODO 네이버 SMS 요청
        """

        return super(UserPasscodeVertifyRequestView, self).post(request, *args, **kwargs)


class UserPasscodeVertifyView(CreateAPIView):
    permission_classes = ()
    serializer_class = serializers.UserPasscodeVertifySerializer

    def post(self, request, *args, **kwargs):
        return super(UserPasscodeVertifyView, self).post(request, *args, **kwargs)


