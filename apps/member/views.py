from django.utils.functional import cached_property
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.member import models
from apps.member import serializers
from apps.member.models import User, UserSNS
from utils.django.rest_framework.mixins import UserContextMixin, QuerySerializerMixin

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
                    "user": {
                        "username": "ozet_d16066f09b594276bb7d9628e5ea1564",
                        "name": "김헤어",
                        "email": "kimhair@hair.com",
                        "phoneNumber": "+821057809397"
                    },
                    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo5LCJ1c2VybmF..",
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


class UserPasscodeVerifyPassView(QuerySerializerMixin, CreateAPIView):
    permission_classes = ()
    serializer_class = serializers.UserPasscodeVerifyPassSerializer
    query_serializer_class = serializers.UserPasscodeVerifyPassSerializer

    @extend_schema(
        tags=[api_tags.PASSCODE],
        summary="패스코드 강제 성공 API @DEBUG",
        description="패스코드 성공했다고 가정하고 바로 JWT를 발행합니다.",
        responses=serializers.UserPasscodeVerifyPassSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="패스코드 강제 성공 API @DEBUG",
                name="201",
                value={
                    "user": {
                        "username": "ozet_d16066f09b594276bb7d9628e5ea1564",
                        "name": "김헤어",
                        "email": "kimhair@hair.com",
                        "phoneNumber": "+821057809397",
                    },
                    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo5LCJ1c2VybmF..",
                },
            ),
            OpenApiExample(
                request_only=True,
                response_only=False,
                name="요청 바디 예시",
                summary="요청 바디 예시",
                description="",
                value={
                    "user_id": "9",
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super(UserPasscodeVerifyPassView, self).post(request, *args, **kwargs)


class UserMeView(UserContextMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.UserMeSerializer

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(UserMeView, self).__init__(*args, **kwargs)

    def get_object(self):
        if getattr(self, "swagger_fake_view", False):
            return None

        return self.user

    @extend_schema(
        tags=[api_tags.USER],
        summary="회원 정보 가져오기 API",
        description="회원 정보 가져오기 API 입니다. @IsAuthenticated",
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
                    "birthday": "1997-7-12",
                    "gender": "male",
                    "introduce": "나는 개쩌는 헤어 디자이너",
                    "address": "경기도 성남시 불라불라",
                    "profileImage": "https://ozet-bucket.s3.ap-northeast-2.amazonaws.com/media/user/profile/5/20211212_25522567",
                    "policyForTermsAgreed": "2021-12-11T07:47:33.336Z",
                    "policyForPrivacyAgreed": "2021-12-11T07:47:33.336Z",
                    "snsList": [
                        {
                            "username": "@bart_not_found",
                            "url": "https://instagram.com/bart_not_found",
                        },
                        {
                            "username": "@bart_not_found",
                            "url": "https://twitter.com/bart_not_found",
                        }
                    ],
                },
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super(UserMeView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER],
        summary="회원 정보 업데이트 API",
        description="회원 정보 업데이트 API 입니다. @IsAuthenticated",
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
                    "birthday": "1997-7-12",
                    "gender": "male",
                    "introduce": "나는 업데이트 된 더욱 개쩌는 헤어 디자이너",
                    "address": "경기도 성남시 불라불라",
                    "profileImage": "https://ozet-bucket.s3.ap-northeast-2.amazonaws.com/media/user/profile/5/20211212_25522567",
                    "policyForTermsAgreed": "2021-12-11T07:47:33.336Z",
                    "policyForPrivacyAgreed": "2021-12-11T07:47:33.336Z",
                    "snsList": [
                        {
                            "username": "@bart_not_found",
                            "url": "https://instagram.com/bart_not_found",
                        },
                        {
                            "username": "@bart_not_found",
                            "url": "https://twitter.com/bart_not_found",
                        }
                    ],
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
                    "introduce": "내가 바로 개쩌는 헤어 디자이너",
                    "address": "경기도 여주시 불라불라",
                    "profileImage": "https://ozet-bucket.s3.ap-northeast-2.amazonaws.com/media/user/profile/5/20211212_25522567",
                    "snsList": [
                        {
                            "username": "@bart_not_found",
                            "url": "https://instagram.com/bart_not_found",
                        },
                        {
                            "username": "@bart_not_found",
                            "url": "https://twitter.com/bart_not_found",
                        }
                    ],
                },
            ),
        ],
    )
    def patch(self, request, *args, **kwargs):
        return super(UserMeView, self).patch(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER],
        summary="회원 정보 삭제 API",
        description="회원 정보 삭제 API 입니다. @IsAuthenticated",
    )
    def delete(self, request, *args, **kwargs):
        return super(UserMeView, self).delete(request, *args, **kwargs)


class UserMeSNSDetailView(UserContextMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.UserSNSDetailSerializer

    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(UserMeSNSDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserSNS.objects.none()

        return UserSNS.objects \
            .filter(resume_id=self.user.resume.id) \
            .order_by('-id') \
            .all()

    @extend_schema(
        tags=[api_tags.USER_SNS],
        summary="회원 SNS 정보 가져오기 API",
        description="회원 SNS 정보 가져오기 API 입니다. @IsAuthenticated",
        responses=serializers.UserMeSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="회원 SNS 정보 가져오기 성공",
                name="200",
                value={
                    "id": 3,
                    "username": "@bart_not_found",
                    "url": "https://instagram.com/bart_not_found",
                },
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super(UserMeSNSDetailView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER_SNS],
        summary="회원 SNS 정보 업데이트 API",
        description="회원 SNS 정보 업데이트 API 입니다. @IsAuthenticated",
        responses=serializers.UserMeSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="회원 정보 업데이트 성공",
                name="200",
                value={
                    "id": 3,
                    "username": "@bart_not_found",
                    "url": "https://instagram.com/bart_not_found",
                },
            ),
            OpenApiExample(
                request_only=True,
                response_only=False,
                name="요청 바디 예시",
                summary="요청 바디 예시",
                description="",
                value={
                    "username": "@bart_not_found",
                    "url": "https://instagram.com/bart_not_found",
                },
            ),
        ],
    )
    def patch(self, request, *args, **kwargs):
        return super(UserMeSNSDetailView, self).patch(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER_SNS],
        summary="회원 SNS 정보 삭제 API",
        description="회원 SNS 정보 삭제 API 입니다. @IsAuthenticated",
    )
    def delete(self, request, *args, **kwargs):
        return super(UserMeSNSDetailView, self).delete(request, *args, **kwargs)


class UserMeSNSListView(UserContextMixin, ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.UserSNSListSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserSNS.objects.none()

        return UserSNS.objects \
            .filter(resume_id=self.user.resume.id) \
            .order_by('-id') \
            .all()

    @extend_schema(
        tags=[api_tags.USER_SNS],
        summary="회원 SNS 정보 목록 가져오기 API",
        description="회원 SNS 정보 가져오기 API 입니다. @IsAuthenticated",
        responses=serializers.UserMeSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(UserMeSNSListView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER_SNS],
        summary="회원 SNS 정보 추가 API",
        description="회원 SNS 정보 추가 API 입니다. @IsAuthenticated",
        responses=serializers.UserMeSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="회원 SNS 정보 추가 성공",
                name="201",
                value={
                    "id": 3,
                    "username": "@bart_not_found",
                    "url": "https://instagram.com/bart_not_found",
                },
            ),
            OpenApiExample(
                request_only=True,
                response_only=False,
                name="요청 바디 예시",
                summary="요청 바디 예시",
                description="",
                value={
                    "username": "@bart_not_found",
                    "url": "https://instagram.com/bart_not_found",
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super(UserMeSNSListView, self).post(request, *args, **kwargs)


class UserTokenLoginView(CreateAPIView):
    permission_classes = ()
    serializer_class = serializers.UserTokenLoginSerializer

    @extend_schema(
        tags=[api_tags.AUTH],
        summary="토큰 로그인 API @DEBUG",
        description="토큰 로그인 API 입니다.",
        responses=serializers.UserTokenLoginSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super(UserTokenLoginView, self).post(request, *args, **kwargs)


class UserTokenRefreshView(UserContextMixin, CreateAPIView):
    permission_classes = ()
    serializer_class = serializers.UserTokenRefreshSerializer

    @extend_schema(
        tags=[api_tags.AUTH],
        summary="토큰 새로고침 API @DEBUG",
        description="토큰 새로고침 API 입니다.",
        responses=serializers.UserTokenRefreshSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super(UserTokenRefreshView, self).post(request, *args, **kwargs)
