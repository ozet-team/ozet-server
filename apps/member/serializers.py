from datetime import timedelta

import jwt
import re
import random
import uuid
from http import HTTPStatus

from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from rest_auth.utils import jwt_encode
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework_jwt.utils import jwt_decode_handler

from django.db import transaction
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

from rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from rest_framework import serializers, fields

from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from apps.member.models import SocialImageCollection, User, UserProfile, UserPasscodeVerify, \
    UserToken, UserSocial
from apps.resume.models import Career
from utils.django.rest_framework.serializers import SimpleSerializer, ModelSerializer
from utils.naver.api import NaverCloudAPI

from apps.member.exceptions import (
    SMSSendError,
    PasscodeVerifyPending,
    PasscodeVerifyInvalidPasscode,
    PasscodeVerifyDoesNotExist,
    UserSignUpError,
    PasscodeVerifyExpired,
)


# noinspection PyAbstractClass
class JWTSerializer(BaseJWTSerializer):
    is_registration = serializers.SerializerMethodField(label=_("첫 가입 여부"), default=False, read_only=True)

    # noinspection PyMethodMayBeStatic
    def get_is_registration(self, obj):
        return getattr(obj.get("user", None), "is_registration", False)


class UserSerializer(ModelSerializer):
    class NestedProfileSerializer(ModelSerializer):
        profile_image = serializers.ImageField(use_url=True)

        class Meta:
            model = UserProfile
            fields = (
                "introduce",
                "profile_image",
                "address",
            )
            read_only_fields = fields

    class NestedUserInstagramSocialSerializer(ModelSerializer):
        class Meta:
            model = UserSocial
            fields = (
                'id',
                'social',
                'social_key',
            )
            read_only_fields = fields

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "email",
            "profile",
            "phone_number",
            "birthday",
            "gender",
            "career",
            "is_registration",
            "social",
        )
        read_only_fields = fields


    profile = NestedProfileSerializer(flatten=True)
    social = NestedUserInstagramSocialSerializer(source='social_set', many=True)
    career = serializers.SerializerMethodField(label=_('경력'), read_only=True)

    # noinspection PyMethodMayBeStatic
    def get_career(self, obj):
        resume = obj.resume
        careers = resume.career_set.all()

        position_list = Career.Position.choices

        career_summary = list()

        for career in careers:
            duration = career.quit_at - career.join_at

            if  duration <= timedelta(30):
                continue

            career_summary.append(dict(position=career.position, duration=duration.days))

        return career_summary


class UserListSerializer(ModelSerializer):
    class NestedUserInstagramSocialSerializer(ModelSerializer):
        class Meta:
            model = UserSocial
            fields = (
                'id',
                'social',
                'social_key',
            )
            read_only_fields = fields

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "profile",
            "phone_number",
            "social",
            "resume",
        )
        read_only_fields = fields

    social = NestedUserInstagramSocialSerializer(source='social_set', many=True)


class UserPasscodeVerifyRequestSerializer(SimpleSerializer):
    class NestedUserPasscodeVerifySerializer(ModelSerializer):
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
    requested_verify = NestedUserPasscodeVerifySerializer(label=_("요청된 인증 상태"), read_only=True)

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
                    user = User.objects.create(
                        username=username,
                        email=None,
                        phone_number=requester_phone_number,
                        name=None,
                    )

            except IntegrityError as e:
                message = str(e)
                # 삭제 계정 복구
                # @TODO: 이미 탈퇴한 회원이 전화번호를 바꾸고 새로운 사람이 가입할 경우에 대한 처리가 필요함
                if 'Duplicate' in message and 'member_user_phone_number' in message:
                    user, _ = User.objects.update_or_create(phone_number=requester_phone_number)

        if not user:
            raise UserSignUpError()

        user_token = user.get_valid_token(UserToken.Type.access, auto_generate=True)
        if not user_token or not user.is_valid_token(user_token.token):
            raise UserSignUpError()

        # 기존 인증 만료 여부
        if UserPasscodeVerify.is_expired(user):
            pass

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

        return dict(requested_verify=self.NestedUserPasscodeVerifySerializer(passcode_verify_request).data)


class UserPasscodeVerifySerializer(SimpleSerializer):
    class NestedUserSerializer(ModelSerializer):
        class Meta:
            model = User
            fields = (
                "id",
                "username",
                "name",
                "email",
                "phone_number",
                "is_registration"
            )

    # Write Only
    phone_number = PhoneNumberField(required=True, allow_blank=False, allow_null=False, write_only=True)
    passcode = fields.CharField(required=True, allow_blank=False, allow_null=False, write_only=True)

    # Read Only
    user = NestedUserSerializer(read_only=True)
    token = fields.CharField(read_only=True)

    # Both

    def validate(self, data):
        return data

    def create(self, validated_data):
        requester_phone_number = validated_data["phone_number"]
        passcode = validated_data["passcode"]

        user = User.objects.get(phone_number=requester_phone_number)

        # 기존 인증 만료 여부
        if UserPasscodeVerify.is_expired(user):
            raise PasscodeVerifyExpired()

        # 유효 인증 존재 여부
        if not UserPasscodeVerify.is_pending(user):
            raise PasscodeVerifyDoesNotExist()

        with transaction.atomic():
            if not UserPasscodeVerify.verify(user, passcode, is_transaction=False):
                raise PasscodeVerifyInvalidPasscode()

        return dict(user=user, token=user.get_valid_token(UserToken.Type.access, auto_generate=True).token)


class UserPasscodeVerifyPassSerializer(SimpleSerializer):
    # Write Only
    user_id = fields.IntegerField(required=True, write_only=True)

    # Read Only
    user = UserSerializer(read_only=True)
    token = fields.CharField(read_only=True)

    # Both

    def validate(self, data):
        data = super(UserPasscodeVerifyPassSerializer, self).validate(data)
        user_id = data['user_id']

        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            raise NotFound()

        data['user'] = user
        data['token'] = user.get_valid_token(UserToken.Type.access, auto_generate=True).token

        return data

    def create(self, validated_data):
        user = validated_data.get('user')
        token = validated_data.get('token')

        return dict(user=user, token=token)


class UserMeSerializer(ModelSerializer):
    class NestedProfileSerializer(ModelSerializer):
        profile_image = serializers.ImageField(use_url=True)

        class Meta:
            model = UserProfile
            fields = (
                "introduce",
                "profile_image",
                "address",
                "policy_for_terms_agreed",
                "policy_for_privacy_agreed",
            )
            read_only_fields = (
                "policy_for_terms_agreed",
                "policy_for_privacy_agreed",
            )

    class NestedUserInstagramSocialSerializer(ModelSerializer):
        class Meta:
            model = UserSocial
            fields = (
                'id',
                'social',
                'social_key',
            )
            read_only_fields = fields

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "email",
            "profile",
            "phone_number",
            "birthday",
            "gender",
            "career",
            "is_registration",
            "social",
        )
        read_only_fields = (
            "id",
            "username",
            "phone_number",
            "career",
            "is_registration",
            "social",
        )

    profile = NestedProfileSerializer(flatten=True)
    social = NestedUserInstagramSocialSerializer(source='social_set', many=True)
    career = serializers.SerializerMethodField(label=_('경력'), read_only=True)

    # noinspection PyMethodMayBeStatic
    def get_career(self, obj):
        resume = obj.resume
        careers = resume.career_set.all()

        position_list = Career.Position.choices

        career_summary = list()

        for career in careers:
            duration = career.quit_at - career.join_at

            if  duration <= timedelta(30):
                continue

            career_summary.append(dict(position=career.position, duration=duration.days))

        return career_summary

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

            # profile_image
            old_profile_image = user_profile.profile_image
            new_profile_image = validated_data.get('profile', {}).get('profile_image', old_introduce)
            if old_profile_image != new_profile_image:
                user_profile.profile_image = new_profile_image
                update_fields.append('profile_image')

            # address
            old_address = user_profile.address
            new_address = validated_data.get('profile', {}).get('address', old_address)
            if old_address != new_address:
                user_profile.address = new_address
                update_fields.append('address')

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

            # gender
            old_gender = instance.gender
            new_gender = validated_data.get('gender', old_gender)
            if old_gender != new_gender:
                instance.gender = new_gender
                update_fields.append('gender')

            # birthday
            old_birthday = instance.birthday
            new_birthday = validated_data.get('birthday', old_birthday)
            if old_birthday != new_birthday:
                instance.birthday = new_birthday
                update_fields.append('birthday')

            if update_fields:
                instance.save(update_fields=update_fields)

            # 유저 SingUp 완료 처리
            if not instance.is_registration:
                instance.is_registration = True
                instance.save(update_fields=['is_registration'])

        return instance


class UserInstagramOAuthSerializer(SimpleSerializer):
    # Write Only
    state = fields.CharField(read_only=True, required=False)


class UserInstagramMediaSerializer(SimpleSerializer):
    # Write Only
    user_id = fields.CharField(read_only=True, required=False)

    # Read Only
    data = fields.CharField(read_only=True)
    paging = fields.CharField(read_only=True)


class UserInstagramProfileSerializer(SimpleSerializer):
    # Write Only
    user_id = fields.CharField(read_only=True, required=False)

    # Read Only
    id = fields.CharField(read_only=True)
    username = fields.CharField(read_only=True)


class UserInstagramSocialSerializer(ModelSerializer):
    class Meta:
        model = UserSocial
        fields = (
            'id',
            'social',
            'social_key',
        )
        read_only_fields = fields


class UserInstagramImageCollectionSerializer(ModelSerializer):
    class Meta:
        model = SocialImageCollection
        fields = (
            'instagram_image_ids',
            'social_user',
            'image_ids',
        )
        read_only_fields = (
            'instagram_image_ids',
            'social_user',
        )

    image_ids = serializers.ListField(
        label='이미지 ID 목록',
        allow_empty=False,
        child=serializers.IntegerField(label='이미지 ID'),
        write_only=True
    )

    def update(self, instance: SocialImageCollection, validated_data):
        image_ids = validated_data.get('image_ids', [])

        if image_ids:
            instance.instagram_image_ids = image_ids
            instance.save(update_fields=['collection_data'])

        return instance


class UserDetailsSerializer(ModelSerializer):
    class NestedProfileSerializer(ModelSerializer):
        profile_image = serializers.ImageField(use_url=True)

        class Meta:
            model = UserProfile
            fields = (
                "introduce",
                "profile_image",
                "policy_for_terms_agreed",
                "policy_for_privacy_agreed",
            )
            read_only_fields = (
                "policy_for_terms_agreed",
                "policy_for_privacy_agreed",
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


class UserTokenLoginSerializer(SimpleSerializer):
    # Write Only
    user_id = fields.IntegerField(required=True, write_only=True)

    # Read Only
    user = UserSerializer(read_only=True)
    access_token = fields.CharField(read_only=True)
    refresh_token = fields.CharField(read_only=True)

    # Both

    def validate(self, data):
        data = super(UserTokenLoginSerializer, self).validate(data)
        user_id = data['user_id']

        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            raise NotFound()

        data['user'] = user
        data['access_token'] = user.get_valid_token(UserToken.Type.access, auto_generate=True).token
        data['refresh_token'] = user.get_valid_token(UserToken.Type.refresh, auto_generate=True).token

        return data

    def create(self, validated_data):
        user = validated_data.get('user')
        access_token = validated_data.get('access_token')
        refresh_token = validated_data.get('refresh_token')

        return dict(access_token=access_token, refresh_token=refresh_token)


class UserTokenRefreshSerializer(SimpleSerializer):
    # Write Only
    refresh_token = serializers.CharField(write_only=True)

    # Read Only
    access_token = fields.CharField(read_only=True)

    # Both

    def validate(self, data):
        data = super(UserTokenRefreshSerializer, self).validate(data)
        refresh_token = data['refresh_token']

        payload = jwt_decode_handler(refresh_token)
        if not payload:
            raise NotFound()

        user = User.objects.filter(id=payload['user_id'], is_active=True).first()
        if not user:
            raise NotFound()

        data['user'] = user
        data['access_token'] = user.get_valid_token(UserToken.Type.access, auto_generate=True).token

        return data

    def create(self, validated_data):
        access_token = validated_data.get('access_token')

        return dict(access_token=access_token)
