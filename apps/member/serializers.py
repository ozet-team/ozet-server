import re
import random
import uuid
from http import HTTPStatus

from rest_auth.utils import jwt_encode
from rest_framework.response import Response

from django.db import transaction
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

from rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from rest_framework import serializers, fields

from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from apps.member.models import User, UserProfile, UserPasscodeVerify, UserToken
from utils.django.rest_framework.serializers import SimpleSerializer, ModelSerializer
from utils.naver.api import NaverCloudAPI

from apps.member.exceptions import (
    SMSSendError,
    PasscodeVerifyPending,
    PasscodeVerifyInvalidPasscode,
    PasscodeVerifyDoesNotExist,
    PasscodeVerifySignUpError, PasscodeVerifyExpired, UserAlreadyUsedEmail,
)


# noinspection PyAbstractClass
class JWTSerializer(BaseJWTSerializer):
    is_registration = serializers.SerializerMethodField(label=_("첫 가입 여부"), default=False, read_only=True)

    # noinspection PyMethodMayBeStatic
    def get_is_registration(self, obj):
        return getattr(obj.get("user", None), "is_registration", False)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone_number"
        )


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "introduce",
            "extra",
        )


class UserPasscodeVerifyRequestSerializer(SimpleSerializer):
    class NestedUserPasscodeVerifyRequestSerializer(ModelSerializer):
        class Meta:
            model = UserPasscodeVerify
            fields = (
                "requester_phone_number",
                "requester_device_uuid",
                "status",
                "expire_at",
            )

    # Write Only
    phone_number = PhoneNumberField(required=True, allow_blank=False, allow_null=False, write_only=True)

    # Read Only
    requested_verify = NestedUserPasscodeVerifyRequestSerializer(label=_("요청된 인증 상태"), read_only=True)

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
        message = f"[OZET] 인증번호: {passcode}\n인증번호를 입력해 주세요."

        res = NaverCloudAPI.send_sms(phone_number, None, message)
        if res.status_code != HTTPStatus.ACCEPTED:
            raise SMSSendError()

        return passcode

    def validate(self, data):
        return data

    def create(self, validated_data):
        requester_phone_number = validated_data["phone_number"]
        user = None

        # 회원 검증
        try:
            user = User.objects.get(phone_number=requester_phone_number)
        except User.DoesNotExist:
            try:
                with transaction.atomic():
                    # Pre-SignUp
                    username = f"ozet_{str(uuid.uuid4()).replace('-', '')}"
                    user = User.objects.update_or_create(
                        username=username,
                        email=None,
                        phone_number=requester_phone_number,
                        name=None,
                    )

                    token = user.get_valid_token(auto_generate=True)
                    if not user.is_valid_token(token.decode("utf-8")):
                        raise PasscodeVerifySignUpError()
            except IntegrityError as e:
                message = str(e)
                # 삭제 계정 복구
                if 'Duplicate' in message and 'member_user_phone_number' in message:
                    user, _ = User.objects.update_or_create(phone_number=requester_phone_number)

        if not user:
            raise PasscodeVerifySignUpError()

        # 중복 인증
        if UserPasscodeVerify.is_pending(user):
            raise PasscodeVerifyPending()

        sent_passcode = self.send_passcode_by_sms(requester_phone_number)

        with transaction.atomic():
            passcode_verify_request = UserPasscodeVerify.objects.create(
                requester_phone_number=requester_phone_number,
                requester_device_uuid=user.username,
                user=user,
                passcode=sent_passcode,
                expire_at=UserPasscodeVerify.get_expire_at(),
            )

        return dict(requested_verify=self.NestedUserPasscodeVerifyRequestSerializer(passcode_verify_request).data)


class UserPasscodeVerifySerializer(SimpleSerializer):
    # Write Only
    phone_number = PhoneNumberField(required=True, allow_blank=False, allow_null=False, write_only=True)
    passcode = fields.CharField(required=True, allow_blank=False, allow_null=False, write_only=True)

    # Read Only
    token = fields.CharField(read_only=True)

    # Both

    def validate(self, data):
        return data

    def create(self, validated_data):
        requester_phone_number = validated_data["phone_number"]
        passcode = validated_data["passcode"]

        user = User.objects.get(phone_number=requester_phone_number)

        # 유효 인증 존재 여부
        if not UserPasscodeVerify.is_pending(user):
            raise PasscodeVerifyDoesNotExist()

        # 기존 인증 만료 여부
        if UserPasscodeVerify.is_expired(user):
            raise PasscodeVerifyExpired()

        with transaction.atomic():
            if not UserPasscodeVerify.verify(user, passcode, is_transaction=False):
                raise PasscodeVerifyInvalidPasscode()

        return dict(token=user.get_valid_token(auto_generate=True).token)


class UserMeSerializer(ModelSerializer):
    class NestedProfileSerializer(ModelSerializer):
        class Meta:
            model = UserProfile
            fields = (
                "introduce",
                "policy_for_terms_agreed",
                "policy_for_privacy_agreed",
                "extra",
            )
            read_only_fields = (
                "policy_for_terms_agreed",
                "policy_for_privacy_agreed",
                "extra",
            )

    class Meta:
        model = User
        fields = (
            "username",
            "name",
            "email",
            "profile",
            "phone_number",
        )
        read_only_fields = (
            "username",
            "phone_number",
        )

    profile = NestedProfileSerializer(flatten=True, read_only=True)

    # noinspection PyMethodMayBeStatic
    def validate_name(self, value):
        if len(value) > 8:
            raise serializers.ValidationError(_('이름은 최대 8글자입니다.'))

        # 한글 / 영어 / 숫자
        result = re.match('[가-힣|a-z|A-Z|0-9]+', value)
        if not result or result.group() != value:
            raise serializers.ValidationError(_('이름은 한글/영어/숫자 조합만 가능합니다.'))

        return value

    def update(self, instance, validated_data):
        user_profile = instance.profile

        with transaction.atomic():
            """
            User Profile Update
            """
            update_fields = []

            # introduce
            old_introduce = user_profile.introduce
            new_introduce = validated_data.get('profile', {}).get('introduce', old_introduce)
            if old_introduce != new_introduce:
                user_profile.introduce = new_introduce
                update_fields.append('introduce')

            if update_fields:
                user_profile.save(update_fields=update_fields)

            """
            User Update
            """
            update_fields = []

            # name
            old_name = instance.name
            new_name = validated_data.get('name', old_name)
            if old_name != new_name:
                instance.name = new_name
                update_fields.append('name')

            # email
            old_email = instance.email
            new_email = validated_data.get('email', old_email)
            if old_email != new_email:
                instance.email = new_email
                update_fields.append('email')

            if update_fields:
                instance.save(update_fields=update_fields)

        return instance


class UserDetailsSerializer(ModelSerializer):
    class NestedProfileSerializer(ModelSerializer):
        class Meta:
            model = UserProfile
            fields = (
                "introduce",
            )
            read_only_fields = (
                "introduce",
            )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "name",
            "created",
            "profile",
            "phone_number",
        )
        read_only_fields = (
            "id",
            "email",
            "username",
            "name",
            "created",
            "profile",
            "phone_number",
        )

    profile = NestedProfileSerializer(flatten=True, read_only=True)

