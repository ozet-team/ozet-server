from django.utils.functional import cached_property
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.member import models
from apps.member import serializers
from apps.member.models import User
from utils.django.rest_framework.mixins import UserContextMixin, QuerySerializerMixin

from commons.contrib.drf_spectacular import tags as api_tags


class UserResumeDetailView(UserContextMixin, RetrieveUpdateDestroyAPIView):
    @extend_schema(
        tags=[api_tags.USER, api_tags.RESUME],
        summary="회원 이력서 가져오기 API",
        description="회원 이력서 가져오기 API 입니다. @JWT",
        responses=serializers.UserMeSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="이력서 가져오기 성공",
                name="201",
                value={
                    "resume": "https://resume.resume",
                    "resume_dataset": "{}",
                },
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super(UserResumeDetailView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER, api_tags.RESUME],
        summary="회원 이력서 추가 API",
        description="회원 이력서 추가 API 입니다. @JWT",
        responses=serializers.UserMeSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="이력서 추가 성공",
                name="201",
                value={
                    "resume": "https://resume.resume",
                    "resume_dataset": "{}",
                },
            ),
        ],
    )
    def put(self, request, *args, **kwargs):
        return super(UserResumeDetailView, self).put(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER, api_tags.RESUME],
        summary="회원 이력서 업데이트 API",
        description="회원 이력서 업데이트 API 입니다. @JWT",
        responses=serializers.UserMeSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="이력서 업데이트 성공",
                name="201",
                value={
                    "resume": "https://resume.resume",
                    "resume_dataset": "{}",
                },
            ),
        ],
    )
    def patch(self, request, *args, **kwargs):
        return super(UserResumeDetailView, self).patch(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER, api_tags.RESUME],
        summary="회원 이력서 삭제 API",
        description="회원 이력서 삭제 API 입니다. @JWT",
    )
    def delete(self, request, *args, **kwargs):
        return super(UserResumeDetailView, self).delete(request, *args, **kwargs)


class ResumeDetailView(UserContextMixin, RetrieveAPIView):
    @extend_schema(
        tags=[api_tags.USER, api_tags.RESUME],
        summary="특정 이력서 가져오기 API",
        description="특정 이력서 가져오기 API 입니다. @DEBUG",
        responses=serializers.UserMeSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="특정 이력서 가져오기 성공",
                name="201",
                value={
                    "resume": "https://resume.resume",
                    "resume_dataset": "{}",
                },
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super(ResumeDetailView, self).get(request, *args, **kwargs)
