# -*- coding: utf-8 -*-
import sentry_sdk
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from drf_yasg.utils import swagger_auto_schema
from firebase_admin import auth as firebase_auth
from firebase_admin import exceptions as firebase_exc
from rest_auth.app_settings import JWTSerializer
from rest_auth.registration.views import SocialLoginView as BaseSocialLoginView
from rest_auth.utils import jwt_encode
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.django.rest_framework.mixin import ClientIPContextMixin
from . import serializers
from ...exceptions import (
    SocialLoginError,
    FacebookLoginError,
    KakaoLoginError,
    NaverLoginError,
    GoogleLoginError,
    AppleLoginError,
)
from ...models import UserToken


# TODO: Enhance API Docs
class SocialLoginView(ClientIPContextMixin,
                      BaseSocialLoginView):
    error_cls = SocialLoginError

    def login(self):
        super(SocialLoginView, self).login()

        # 토큰 확인
        # TODO: 디바이스별로 토큰 생성되도록 개선
        token = getattr(self, 'token', None)
        if not token:
            return
        user_agent = self.request.META.get('HTTP_USER_AGENT', None)
        user_ip = self.client_ip

        if UserToken.objects.filter(token=token).exists():
            return

        UserToken.objects.create(
            user=self.user,
            token=token,
            user_agent=user_agent,
            user_ip=user_ip
        )

    @swagger_auto_schema(tags=[constants.MEMBER_AUTH_APIS_TAG])
    def post(self, request, *args, **kwargs):
        # noinspection PyAttributeOutsideInit
        self.serializer = self.get_serializer(data=self.request.data)
        try:
            self.serializer.is_valid(raise_exception=True)
        except Exception:
            sentry_sdk.capture_exception()
            raise self.error_cls()
        self.login()
        return self.get_response()


class FacebookLoginAPIView(SocialLoginView):
    """
    post:
    Facebook 로그인 API
    """

    adapter_class = FacebookOAuth2Adapter

    error_cls = FacebookLoginError


class KakaoLoginAPIView(SocialLoginView):
    """
    post:
    Kakao 로그인 API
    """

    adapter_class = KakaoOAuth2Adapter

    error_cls = KakaoLoginError


class NaverLoginAPIView(SocialLoginView):
    """
    post:
    Naver 로그인 API
    """

    adapter_class = NaverOAuth2Adapter

    error_cls = NaverLoginError


class GoogleLoginAPIView(SocialLoginView):
    """
    post:
    Google 로그인 API
    """

    adapter_class = GoogleOAuth2Adapter

    error_cls = GoogleLoginError


class AppleLoginAPIView(SocialLoginView):
    """
    post:
    Apple 로그인 API
    """

    adapter_class = AppleOAuth2Adapter

    serializer_class = serializers.AppleLoginSerializer

    error_cls = AppleLoginError


class LogoutAPIView(APIView):
    """
    post:
    로그아웃 API
    """

    @swagger_auto_schema(tags=[constants.MEMBER_AUTH_APIS_TAG])
    def post(self, request, *args, **kwargs):
        jwt_value = getattr(request, 'jwt_value', None)
        if not jwt_value:
            return Response({}, status=status.HTTP_200_OK)

        user = self.request.user

        # 토큰 제거
        user.token_set.filter(token=jwt_value.decode('utf-8')).delete()

        # Firebase Token Revoke
        try:
            firebase_auth.revoke_refresh_tokens(uid=str(user.id))
        except (firebase_auth.UserNotFoundError, firebase_exc.UnauthenticatedError):
            pass
        return Response({}, status=status.HTTP_200_OK)
