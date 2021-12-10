import re

from typing import Union, Literal, Optional

from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

import time
import requests
import hashlib
import hmac
import base64

from requests import Response

PROJECT_SERVICE_ID = "ncp:sms:kr:256400342331:ozet_sms_module"
ACCESS_KEY = "9h0R0dOkMEGRNAOTTthX"
SECRET_KEY = "1eHqKPKw0F2LDBteRTILWOwVCkQixo8x2WrUE722"

CALLER_ID = '01057809397'


def is_valid_phonenumber(phone_number: str) -> bool:
    return bool(re.match('\d{2,3}\d{3,4}\d{4}', phone_number))


def get_timestamp():
    return str(int(time.time() * 1000))


def make_signature(
        method: Literal['POST', 'GET'],
        uri: str,
        timestmap: str,
        access_key: str = ACCESS_KEY,
        secret_key: str = SECRET_KEY
):
    """
    네이버 API Signature 생성

    Args:
        method:
        uri:
        timestmap:
        access_key:
        secret_key:

    Returns:
        siging_key:

    Notes:

    """
    secret_key = bytes(secret_key, 'UTF-8')

    message = method + " " + uri + "\n" + timestmap + "\n" + access_key
    message = bytes(message, 'UTF-8')

    siging_key = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

    return siging_key


class NaverCloudAPI(object):
    @classmethod
    def send_sms(
            cls,
            phone_number: Union[str, PhoneNumber],
            subject: Optional[str],
            message: str
    ) -> Response:
        """
        Naver SMS 문자 발송

        Args:
            phone_number: 발송할 전화번호
            subject: SMS 제목
            message: SMS 내용

        Returns:
            response: 네이버 API 응답

        Notes:

        """
        if isinstance(phone_number, PhoneNumber):
            phone_number = str(phone_number.as_national.replace('-', ''))

        if not is_valid_phonenumber(phone_number):
            raise ValueError

        #  URL
        url = f'https://sens.apigw.ntruss.com/sms/v2/services/{PROJECT_SERVICE_ID}/messages'

        # uri
        uri = f'/sms/v2/services/{PROJECT_SERVICE_ID}/messages'
        timestamp = get_timestamp()

        body = {
            "type": "SMS",
            "contentType": "COMM",
            "countryCode": "82",
            "from": CALLER_ID,
            "content": message,
            "messages": [
                {
                    "to": phone_number,
                    "subject": subject,
                    "content": message
                }
            ]
        }

        key = make_signature('POST', uri, timestamp)
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': ACCESS_KEY,
            'x-ncp-apigw-signature-v2': key
        }

        return requests.post(url, json=body, headers=headers)
