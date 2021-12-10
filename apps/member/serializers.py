import random
import uuid
from http import HTTPStatus

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from rest_framework import serializers, fields

from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from apps.member.models import User, UserProfile, UserPasscodeVertify
from utils.django.rest_framework.serializers import SimpleSerializer, ModelSerializer
from utils.naver.api import NaverCloudAPI

from apps.member.exceptions import (
    SMSSendError, PasscodeVertifyPending, PasscodeVertifyInvalidPasscode,
)


# noinspection PyAbstractClass
class JWTSerializer(BaseJWTSerializer):
    is_registration = serializers.SerializerMethodField(label=_('첫 가입 여부'), default=False, read_only=True)

    # noinspection PyMethodMayBeStatic
    def get_is_registration(self, obj):
        return getattr(obj.get('user', None), 'is_registration', False)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone_number"
        ]


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "introduce",
            "extra",
        ]


class UserPasscodeVertifyRequestSerializer(SimpleSerializer):
    class NestedUserPasscodeVertifyRequestSerializer(ModelSerializer):
        class Meta:
            model = UserPasscodeVertify
            fields = [
                "requester_phone_number",
                "requsster_device_uuid",
                "status",
            ]

    # Write Only
    phone_number = PhoneNumberField(required=True, allow_blank=False, allow_null=False, write_only=True)

    # Read Only
    requested_passcode_vertify = NestedUserPasscodeVertifyRequestSerializer(read_only=True)

    # Both

    # noinspection PyMethodMayBeStatic
    def passcode_generate(self) -> int:
        """
            패스코드 6자리를 생성해서 반환

        Returns:
            passcode: 패스코드 6자리
        """
        return random.randint(100000, 999999)

    def send_passcode_by_sms(self, phone_number: PhoneNumber):
        """
        Args:
            phone_number: 패스코드를 발송할 전화번호

        Returns:
            response: Naver API 응답
        """
        passcode = self.passcode_generate()
        message = f'[OZET] 인증번호: {passcode}\n인증번호를 입력해 주세요.'

        res = NaverCloudAPI.send_sms(phone_number, None, message)
        if res.status_code != HTTPStatus.ACCEPTED:
            raise SMSSendError()

        return passcode

    def validate(self, data):
        return data

    def create(self, validated_data):
        requester_phone_number = validated_data['phone_number']

        sended_passcode = self.send_passcode_by_sms(requester_phone_number)

        with transaction.atomic():
            # 사용자 인증
            try:
                user = User.objects.get(phone_number=requester_phone_number)
            except User.DoesNotExist:
                # Pre-SingUp
                user = User.objects.create(
                    username=f'ozet_{uuid.uuid4()}',
                    email=None,
                    phone_number=requester_phone_number,
                    name=None,
                )
                user.save()

            # 중복 인증
            if UserPasscodeVertify.is_pending(user):
                raise PasscodeVertifyPending()

            passcode_vertify_request = UserPasscodeVertify.objects.create(
                requester_phone_number=requester_phone_number,
                requsster_device_uuid=user.username,
                user=user,
                passcode=sended_passcode,
            )

        return validated_data


class UserPasscodeVertifySerializer(SimpleSerializer):
    # Write Only
    phone_number = PhoneNumberField(required=True, allow_blank=False, allow_null=False, write_only=True)
    passcode = fields.CharField(required=True, allow_blank=False, allow_null=False, write_only=True)

    # Read Only

    # Both

    def validate(self, data):
        return data

    def create(self, validated_data):
        requester_phone_number = validated_data['phone_number']

        user = User.objects.get(phone_number=requester_phone_number)

        with transaction.atomic():
            if not UserPasscodeVertify.vertify(user):
                raise PasscodeVertifyInvalidPasscode()

        return validated_data

