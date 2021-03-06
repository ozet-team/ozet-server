from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class SMSSendError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('문자 인증 발송에 실패했습니다.')


class UserSignUpError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('회원 정보 생성중에 문제가 생겼습니다.')


class PasscodeVerifyPending(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('이미 요청 대기중인 인증이 있습니다.')


class PasscodeVerifyDoesNotExist(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('유효한 인증 요청이 존재하지 않습니다.')


class PasscodeVerifyInvalidPasscode(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('일치하지 않는 패스코드입니다.')


class PasscodeVerifyExpired(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('기존 인증 요청이 만료되었습니다. 다시 시도해주세요.')

