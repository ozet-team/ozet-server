from utils.django.rest_framework.serializers import SimpleSerializer, ModelSerializer
from rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from rest_framework import serializers
from apps.member.models import User, UserProfile, UserPasscodeVertify


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
    def create(self, validated_data):
        return validated_data


class UserPasscodeVertifySerializer(SimpleSerializer):
    def create(self, validated_data):
        return validated_data

