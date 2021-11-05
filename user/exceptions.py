# -*- coding: utf-8 -*-
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class EmailLoginError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('이메일 인증 정보를 가져오지 못했습니다. 잠시후 다시 시도해주세요.')


class SocialLoginError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('소셜 서비스에서 인증 정보를 가져오지 못했습니다. 잠시후 다시 시도해주세요.')


class FacebookLoginError(SocialLoginError):
    default_detail = _('페이스북에서 인증 정보를 가져오지 못했습니다. 잠시후 다시 시도해주세요.')


class KakaoLoginError(SocialLoginError):
    default_detail = _('카카오에서 인증 정보를 가져오지 못했습니다. 잠시후 다시 시도해주세요.')


class NaverLoginError(SocialLoginError):
    default_detail = _('네이버에서 인증 정보를 가져오지 못했습니다. 잠시후 다시 시도해주세요.')


class GoogleLoginError(SocialLoginError):
    default_detail = _('구글에서 인증 정보를 가져오지 못했습니다. 잠시후 다시 시도해주세요.')


class AppleLoginError(SocialLoginError):
    default_detail = _('애플에서 인증 정보를 가져오지 못했습니다. 잠시후 다시 시도해주세요.')


class FirebaseLoginError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('외부 서비스 연동에 실패했습니다. 잠시후 다시 시도해주세요.')


class UserDuplicatedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('해당 계정으로 이미 가입되어 있습니다.')


class UserNotFoundError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('해당 계정으로 가입되어 있지 않습니다.')


class UserSingUpError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('해당 계정으로 가입할 수 없습니다.\n채티로 문의해주세요.')


class UserReSignUpError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('재가입은 탈퇴후 15일이 지난후부터 가능합니다.')


class UserEmailVerifiedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('해당 계정은 이미 이메일 인증이 되어있습니다.')
