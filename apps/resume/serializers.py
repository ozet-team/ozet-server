import re
import random
import uuid
from http import HTTPStatus

from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from rest_auth.utils import jwt_encode
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from django.db import transaction
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

from rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from rest_framework import serializers, fields

from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from apps.resume.models import Resume, Career, Certificate, AcademicBackground, MilitaryService
from utils.django.rest_framework.serializers import SimpleSerializer, ModelSerializer


class CareerSerializer(ModelSerializer):
    class Meta:
        model = Career
        fields = (
            'id',
            'company',
            'position',
            'join_at',
            'quit_at',
            'worked_on',
        )

        read_only_fields = ()

    def create(self, validated_data):
        user = self.context['user']
        career = Career.objects.create(resume=user.resume, **validated_data)

        return career


class CertificateSerializer(ModelSerializer):
    class Meta:
        model = Certificate
        fields = (
            'id',
            'name',
            'vendor',
            'certificate_at',
        )

        read_only_fields = ()

    def create(self, validated_data):
        user = self.context['user']
        certificate = Certificate.objects.create(resume=user.resume, **validated_data)

        return certificate


class AcademicBackgroundSerializer(ModelSerializer):
    class Meta:
        model = AcademicBackground
        fields = (
            'id',
            'name',
            'major',
            'location',
            'join_at',
            'quit_at',
        )

        read_only_fields = ()

    def create(self, validated_data):
        user = self.context['user']
        academic_background = AcademicBackground.objects.create(resume=user.resume, **validated_data)

        return academic_background


class MilitaryServiceSerializer(ModelSerializer):
    class Meta:
        model = MilitaryService
        fields = (
            'id',
            'service',
            'exemption_reason',
            'join_at',
            'quit_at',
        )

        read_only_fields = ()

    def create(self, validated_data):
        user = self.context['user']
        military_service = MilitaryService.objects.create(resume=user.resume, **validated_data)

        return military_service


class ResumeSerializer(ModelSerializer):
    class Meta:
        model = Resume
        fields = (
            "id",
            "career",
            "certificate",
            "academic",
            "military",
            "pdf_file"
        )

    career = CareerSerializer(many=True, source='career_set')
    certificate = CertificateSerializer(many=True, source='certificate_set')
    academic = AcademicBackgroundSerializer(many=True, source='academic_set')
    military = MilitaryServiceSerializer()


class UserResumeSerializer(ModelSerializer):
    class Meta:
        model = Resume
        fields = (
            "id",
            "career",
            "certificate",
            "academic",
            "military",
            "pdf_file"
        )

    career = CareerSerializer(many=True, source='career_set')
    certificate = CertificateSerializer(many=True, source='certificate_set')
    academic = AcademicBackgroundSerializer(many=True, source='academic_set')
    military = MilitaryServiceSerializer()


class ResumePDFSerializer(ModelSerializer):
    class Meta:
        model = Resume
        fields = (
            "id",
            "pdf_file",
        )
