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

PROJECT_SERVICE_ID = "658909912196679"
PROJECT_SERVICE_NAME = "ozet"
SECRET_KEY = "9421262ee369d46bb82c372db0bf3c8e"

class InstagramAPI(object):
    @classmethod
    def auth(
            cls,
            redirect_uri="http://localhost:8000"
    ) -> Response:
        """
        Instagram Token Auth

        Args:

        Returns:
            response: 네이버 API 응답

        Notes:
            https://api.instagram.com/oauth/authorize
              ?client_id={app-id}
              &redirect_uri={redirect-uri}
              &scope=user_profile,user_media
              &response_type=code
        """
        #  URL
        url = f'https://api.instagram.com/oauth/authorize?client_id={PROJECT_SERVICE_ID}&redirect_uri={redirect_uri}&scope=user_profile,user_media&response_type=code'

        return requests.get(url)
