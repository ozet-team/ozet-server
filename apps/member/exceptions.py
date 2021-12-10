from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class SMSSendError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('문자 인증 발송에 실패했습니다.')


class PasscodeVertifyPending(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('이미 요청 대기중인 인증이 있습니다.')


class PasscodeVertifyInvalidPasscode(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('일치하지 않는 패스코드입니다.')