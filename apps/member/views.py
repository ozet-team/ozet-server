from django.utils.functional import cached_property
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.member import models
from apps.member import serializers
from utils.django.rest_framework.mixins import UserContextMixin

from commons.contrib.drf_spectacular import tags as api_tags


class UserPasscodeVerifyRequestView(CreateAPIView):
    permission_classes = ()
    serializer_class = serializers.UserPasscodeVerifyRequestSerializer

    @extend_schema(
        tags=[api_tags.PASSCODE],
        summary="패스코드 인증 요청 API",
        description="패스코드 인증 요청 API 입니다.",
        responses=serializers.UserPasscodeVerifyRequestSerializer,
        request=serializers.UserPasscodeVerifyRequestSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="패스코드 인증 요청 성공",
                name="201",
                value={
                  "requestedVerify": {
                    "requesterPhoneNumber": "+821057809397",
                    "requesterDeviceUuid": "ozet_d16066f09b594276bb7d9628e5ea1564",
                    "status": "pending",
                    "expireAt": "2021-12-11T06:30:47.390Z"
                  }
                },
            ),
            OpenApiExample(
                request_only=True,
                response_only=False,
                name="요청 바디 예시",
                summary="요청 바디 예시",
                description="전화번호 포맷은 E164를 사용합니다.[https://www.twilio.com/docs/glossary/what-e164]",
                value={
                    "phoneNumber": "+821057809397",
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super(UserPasscodeVerifyRequestView, self).post(request, *args, **kwargs)


class UserPasscodeVerifyView(CreateAPIView):
    permission_classes = ()
    serializer_class = serializers.UserPasscodeVerifySerializer

    @extend_schema(
        tags=[api_tags.PASSCODE],
        summary="패스코드 인증 API",
        description="패스코드 인증 API 입니다.",
        responses=serializers.UserPasscodeVerifySerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="패스코드 인증 요청 성공",
                name="201",
                value={
                    "token": ""
                },
            ),
            OpenApiExample(
                request_only=True,
                response_only=False,
                name="요청 바디 예시",
                summary="요청 바디 예시",
                description="전화번호 포맷은 E164를 사용합니다.[https://www.twilio.com/docs/glossary/what-e164]",
                value={
                    "phoneNumber": "+821057809397",
                    "passcode": "958322",
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super(UserPasscodeVerifyView, self).post(request, *args, **kwargs)


class UserMeView(UserContextMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.UserMeSerializer

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(UserMeView, self).__init__(*args, **kwargs)

    @cached_property
    def get_object(self):
        if getattr(self, "swagger_fake_view", False):
            return None

        return self.user

    @extend_schema(
        tags=[api_tags.USER],
        summary="회원 정보 가져오기 API",
        description="회원 정보 가져오기 API 입니다. @JWT",
        responses=serializers.UserMeSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="회원 정보 가져오기 성공",
                name="201",
                value={
                    "username": "ozet_d16066f09b594276bb7d9628e5ea1564",
                    "name": "김헤어",
                    "email": "kimhair@hair.com",
                    "phoneNumber": "+821057809397",
                    "introduce": "나는 개쩌는 헤어 디자이너",
                    "policyForTermsAgreed": "2021-12-11T07:47:33.336Z",
                    "policyForPrivacyAgreed": "2021-12-11T07:47:33.336Z",
                },
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super(UserMeView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER],
        summary="회원 정보 업데이트 API",
        description="회원 정보 업데이트 API 입니다. @JWT",
        responses=serializers.UserMeSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="회원 정보 업데이트 성공",
                name="200",
                value={
                    "username": "ozet_d16066f09b594276bb7d9628e5ea1564",
                    "name": "김헤어",
                    "email": "kimhair@hair.com",
                    "phoneNumber": "+821057809397",
                    "introduce": "나는 업데이트 된 더욱 개쩌는 헤어 디자이너",
                    "policyForTermsAgreed": "2021-12-11T07:47:33.336Z",
                    "policyForPrivacyAgreed": "2021-12-11T07:47:33.336Z",
                },
            ),
            OpenApiExample(
                request_only=True,
                response_only=False,
                name="요청 바디 예시",
                summary="요청 바디 예시",
                description="",
                value={
                    "name": "김헤어",
                    "email": "kimhair@hair.com",
                    "introduce": "내가 바로 개쩌는 헤어 디자이너"
                },
            ),
        ],
    )
    def patch(self, request, *args, **kwargs):
        return super(UserMeView, self).patch(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER],
        summary="회원 정보 삭제 API",
        description="회원 정보 삭제 API 입니다. @JWT",
    )
    def delete(self, request, *args, **kwargs):
        return super(UserMeView, self).delete(request, *args, **kwargs)

