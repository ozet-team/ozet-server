from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class SMSSendError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('문자 인증 발송에 실패했습니다.')