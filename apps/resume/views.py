from django.utils.functional import cached_property
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.exceptions import NotFound

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
)
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from apps.member.models import User
from apps.resume import models
from apps.resume import serializers
from apps.resume.models import Career, Certificate, AcademicBackground, MilitaryService, Resume
from utils.django.rest_framework.mixins import UserContextMixin, QuerySerializerMixin

from commons.contrib.drf_spectacular import tags as api_tags


class ResumeDetailView(UserContextMixin, RetrieveAPIView):
    permission_classes = (AllowAny, )
    serializer_class = serializers.ResumeSerializer

    queryset = Resume.objects
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    @extend_schema(
        tags=[api_tags.RESUME],
        summary="회원 이력서 가져오기 API @AllowAny",
        description="회원 이력서 가져오기 API 입니다.",
        responses=serializers.ResumeSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(ResumeDetailView, self).get(request, *args, **kwargs)


class UserResumeDetailView(UserContextMixin, RetrieveAPIView):
    permission_classes = (AllowAny, )
    serializer_class = serializers.UserResumeSerializer

    def get_object(self):
        user_id = self.kwargs.get('user_id', None)
        if not user_id:
            raise NotFound()

        return get_object_or_404(Resume, user_id=user_id)

    @extend_schema(
        tags=[api_tags.RESUME],
        summary="회원 이력서 가져오기 API @AllowAny",
        description="회원 이력서 가져오기 API 입니다.",
        responses=serializers.UserResumeSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(UserResumeDetailView, self).get(request, *args, **kwargs)


class UserMeResumeDetailView(UserContextMixin, RetrieveAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.ResumeSerializer

    def get_object(self):
        resume, is_created = Resume.objects.get_or_create(user_id=self.user.id)

        return resume

    @extend_schema(
        tags=[api_tags.USER_ME],
        summary="회원 이력서 가져오기 API @IsAuthenticated",
        description="회원 이력서 가져오기 API 입니다.",
        responses=serializers.ResumeSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(UserMeResumeDetailView, self).get(request, *args, **kwargs)


class UserMeResumeDetailPDFView(UserContextMixin, RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.ResumePDFSerializer

    def get_object(self):
        resume, is_created = Resume.objects.get_or_create(user_id=self.user.id)

        return resume

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put" and method != "get"]
        super(UserMeResumeDetailPDFView, self).__init__(*args, **kwargs)

    @extend_schema(
        tags=[api_tags.USER_ME],
        summary="회원 이력서 PDF 업데이트 API @IsAuthenticated",
        description="회원 이력서 PDF 업데이트 API 입니다.",
        responses=serializers.ResumePDFSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super(UserMeResumeDetailPDFView, self).patch(request, *args, **kwargs)


class ResumeCareerDetailView(UserContextMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.CareerSerializer

    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(ResumeCareerDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Career.objects.none()

        return Career.objects \
            .filter(resume_id=self.user.resume.id) \
            .order_by('-join_at') \
            .all()

    @extend_schema(
        tags=[api_tags.RESUME_CAREER],
        summary="회원 커리어 가져오기 API @IsAuthenticated",
        description="회원 커리어 가져오기 API 입니다.",
        responses=serializers.CareerSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(ResumeCareerDetailView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_CAREER],
        summary="회원 커리어 업데이트 API @IsAuthenticated",
        description="회원 커리어 업데이트 API 입니다.",
        responses=serializers.CareerSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super(ResumeCareerDetailView, self).patch(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_CAREER],
        summary="회원 커리어 삭제 API @IsAuthenticated",
        description="회원 커리어 삭제 API 입니다.",
    )
    def delete(self, request, *args, **kwargs):
        return super(ResumeCareerDetailView, self).delete(request, *args, **kwargs)


class ResumeCareerListView(UserContextMixin, ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.CareerSerializer

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(ResumeCareerListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Career.objects.none()

        return Career.objects \
            .filter(resume_id=self.user.resume.id) \
            .order_by('-join_at') \
            .all()

    @extend_schema(
        tags=[api_tags.RESUME_CAREER],
        summary="회원 커리어 가져오기 API @IsAuthenticated",
        description="회원 커리어 가져오기 API 입니다.\n"
                    "* **Position**\n"
                    "    * **STAFF** - 스탭(인턴)\n"
                    "    * **MANAGER** - 매니저\n"
                    "    * **DESIGNER** - 디자이너\n"
                    "    * **DIRECTOR** - 원장",
        responses=serializers.CareerSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(ResumeCareerListView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_CAREER],
        summary="회원 커리어 추가 API @IsAuthenticated",
        description="회원 커리어 추가 API 입니다.\n"
                    "* **Position**\n"
                    "    * **STAFF** - 스탭(인턴)\n"
                    "    * **MANAGER** - 매니저\n"
                    "    * **DESIGNER** - 디자이너\n"
                    "    * **DIRECTOR** - 원장",
        responses=serializers.CareerSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super(ResumeCareerListView, self).post(request, *args, **kwargs)


class ResumeCertificateDetailView(UserContextMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.CertificateSerializer

    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(ResumeCertificateDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Certificate.objects.none()

        return Certificate.objects \
            .filter(resume_id=self.user.resume.id) \
            .order_by('-certificate_at') \
            .all()

    @extend_schema(
        tags=[api_tags.RESUME_CERTIFICATE],
        summary="회원 자격증 가져오기 API @IsAuthenticated",
        description="회원 자격증 가져오기 API 입니다.",
        responses=serializers.CertificateSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(ResumeCertificateDetailView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_CERTIFICATE],
        summary="회원 자격증 업데이트 API @IsAuthenticated",
        description="회원 자격증 업데이트 API 입니다.",
        responses=serializers.CertificateSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super(ResumeCertificateDetailView, self).patch(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_CERTIFICATE],
        summary="회원 자격증 삭제 API @IsAuthenticated",
        description="회원 자격증 삭제 API 입니다.",
    )
    def delete(self, request, *args, **kwargs):
        return super(ResumeCertificateDetailView, self).delete(request, *args, **kwargs)


class ResumeCertificateListView(UserContextMixin, ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.CertificateSerializer

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(ResumeCertificateListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Certificate.objects.none()

        return Certificate.objects \
            .filter(resume_id=self.user.resume.id) \
            .order_by('-certificate_at') \
            .all()

    @extend_schema(
        tags=[api_tags.RESUME_CERTIFICATE],
        summary="회원 자격증 목록 가져오기 API @IsAuthenticated",
        description="회원 자격증 목록 가져오기 API 입니다.",
        responses=serializers.CertificateSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(ResumeCertificateListView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_CERTIFICATE],
        summary="회원 자격증 추가 API @IsAuthenticated",
        description="회원 자격증 추가 API 입니다.",
        responses=serializers.CertificateSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super(ResumeCertificateListView, self).post(request, *args, **kwargs)


class ResumeAcademicBackgroundDetailView(UserContextMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.AcademicBackgroundSerializer

    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(ResumeAcademicBackgroundDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AcademicBackground.objects.none()

        return AcademicBackground.objects \
            .filter(resume_id=self.user.resume.id) \
            .order_by('-join_at') \
            .all()

    @extend_schema(
        tags=[api_tags.RESUME_ACADEMIC],
        summary="회원 학력 가져오기 API @IsAuthenticated",
        description="회원 학력 가져오기 API 입니다.",
        responses=serializers.AcademicBackgroundSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(ResumeAcademicBackgroundDetailView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_ACADEMIC],
        summary="회원 학력 업데이트 API @IsAuthenticated",
        description="회원 학력 업데이트 API 입니다.",
        responses=serializers.AcademicBackgroundSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super(ResumeAcademicBackgroundDetailView, self).patch(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_ACADEMIC],
        summary="회원 학력 삭제 API @IsAuthenticated",
        description="회원 학력 삭제 API 입니다.",
    )
    def delete(self, request, *args, **kwargs):
        return super(ResumeAcademicBackgroundDetailView, self).delete(request, *args, **kwargs)


class ResumeAcademicBackgroundListView(UserContextMixin, ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.AcademicBackgroundSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AcademicBackground.objects.none()

        return AcademicBackground.objects \
            .filter(resume_id=self.user.resume.id) \
            .order_by('-join_at') \
            .all()

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(ResumeAcademicBackgroundListView, self).__init__(*args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_ACADEMIC],
        summary="회원 학력 목록 가져오기 API @IsAuthenticated",
        description="회원 학력 목록 가져오기 API 입니다.",
        responses=serializers.AcademicBackgroundSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(ResumeAcademicBackgroundListView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_ACADEMIC],
        summary="회원 학력 추가 API @IsAuthenticated",
        description="회원 학력 추가 API 입니다.",
        responses=serializers.AcademicBackgroundSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super(ResumeAcademicBackgroundListView, self).post(request, *args, **kwargs)


class ResumeMilitaryServiceView(UserContextMixin, RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.MilitaryServiceSerializer

    def get_object(self):
        military, is_created = MilitaryService.objects.get_or_create(resume_id=self.user.resume.id)

        return military

    def __init__(self, *args, **kwargs):
        self.http_method_names = [method for method in self.http_method_names if method != "put"]
        super(ResumeMilitaryServiceView, self).__init__(*args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_MILITARY],
        summary="회원 병역 가져오기 API @IsAuthenticated",
        description="회원 병역 가져오기 API 입니다.\n"
                    "* **Service Status**\n"
                    "    * **NA** - 해당없음\n"
                    "    * **EXEMPTION** - 면제\n"
                    "    * **UNFINISHED** - 미필\n"
                    "    * **FINISHED** - 군필",
        responses=serializers.MilitaryServiceSerializer,
    )
    def get(self, request, *args, **kwargs):
        return super(ResumeMilitaryServiceView, self).get(request, *args, **kwargs)

    @extend_schema(
        tags=[api_tags.RESUME_MILITARY],
        summary="회원 병역 업데이트 API @IsAuthenticated",
        description="회원 병역 업데이트 API 입니다.\n"
                    "* **Service Status**\n"
                    "    * **NA** - 해당없음\n"
                    "    * **EXEMPTION** - 면제\n"
                    "    * **UNFINISHED** - 미필\n"
                    "    * **FINISHED** - 군필",
        responses=serializers.MilitaryServiceSerializer,
    )
    def patch(self, request, *args, **kwargs):
        return super(ResumeMilitaryServiceView, self).patch(request, *args, **kwargs)
