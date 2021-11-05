# -*- coding: utf-8 -*-

from allauth.account import app_settings as allauth_settings
from allauth.socialaccount.helpers import complete_social_login
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext_lazy as _
from requests import HTTPError
from rest_auth.registration.serializers import SocialLoginSerializer
from rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from rest_framework import fields, serializers
from rest_framework.exceptions import NotFound, AuthenticationFailed

from utils.django.rest_framework.serializers import ModelSerializer
from ...models import User


class TestLoginSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', )

    # WRITE ONLY
    user_id = fields.IntegerField(write_only=True, required=True)

    def validate(self, attrs):
        attrs = super(TestLoginSerializer, self).validate(attrs)
        user_id = attrs['user_id']
        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            raise NotFound()
        attrs['user'] = user
        return attrs


class UsernameLoginSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'password'
        )

    username = fields.CharField(required=True, allow_blank=False)
    password = fields.CharField(required=True, write_only=True, allow_blank=False)

    def validate(self, attrs):
        attrs = super(UsernameLoginSerializer, self).validate(attrs)
        username = attrs['username']
        user = User.objects.filter(username=username).first()
        if not user:
            raise AuthenticationFailed()

        password = attrs['password']
        if not check_password(password, user.password):
            raise AuthenticationFailed()

        attrs['user'] = user
        return attrs


# noinspection PyAbstractClass
class JWTSerializer(BaseJWTSerializer):
    is_registration = serializers.SerializerMethodField(label=_('첫 가입 여부'), default=False, read_only=True)

    # noinspection PyMethodMayBeStatic
    def get_is_registration(self, obj):
        return getattr(obj.get('user', None), 'is_registration', False)


# noinspection PyAbstractClass
class AppleLoginSerializer(SocialLoginSerializer):
    code = None
    access_token = serializers.CharField(required=True, allow_blank=False)
    id_token = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs):
        view = self.context.get('view')
        request = self._get_request()

        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable")
            )

        adapter_class = getattr(view, 'adapter_class', None)
        if not adapter_class:
            raise serializers.ValidationError(_("Define adapter_class in view"))

        adapter = adapter_class(request)
        app = adapter.get_provider().get_app(request)

        access_token = attrs.get('access_token')
        id_token = attrs.get('id_token')
        if access_token is None or id_token is None:
            raise serializers.ValidationError(
                _("Incorrect input. access_token or code is required."))

        social_token = adapter.parse_token({
            'access_token': access_token,
            'id_token': id_token,
        })
        social_token.app = app

        try:
            login = self.get_social_login(adapter, app, social_token, access_token)
            complete_social_login(request, login)
        except HTTPError:
            raise serializers.ValidationError(_("Incorrect value"))

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            if allauth_settings.AppSettings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
                account_exists = get_user_model().objects.filter(
                    email=login.user.email,
                ).exists()
                if account_exists:
                    raise serializers.ValidationError(
                        _("User is already registered with this e-mail address.")
                    )

            login.lookup()
            login.save(request, connect=True)

        attrs['user'] = login.account.user

        return attrs
