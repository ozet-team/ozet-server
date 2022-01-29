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
API_VERSION = "v12.0"

"""
https://api.ozet.app/api/v1/member/user/me/instagram/oauth/authorize

https://staging-api.ozet.app/api/v1/member/user/me/instagram/oauth/authorize
https://staging-api.ozet.app/api/v1/member/user/me/instagram/oauth/cancel
https://staging-api.ozet.app/api/v1/member/user/me/instagram/oauth/delete

https://df45-211-37-41-64.ngrok.io /api/v1/member/user/me/instagram/oauth/authorize
https://dbce-125-131-185-253.ngrok.io/api/v1/member/user/me/instagram/oauth/cancel
https://dbce-125-131-185-253.ngrok.io/api/v1/member/user/me/instagram/oauth/delete

"""
class InstagramAPI(object):
    @classmethod
    def oauth(
            cls,
            state: str ,
            redirect_uri: str = "http://localhost:8000"
    ) -> Response:
        """
        Instagram Token Auth

        Args:

        Returns:
            response: Instagram API 응답

        Notes:
            https://api.instagram.com/oauth/authorize
              ?client_id={app-id}
              &redirect_uri={redirect-uri}
              &scope=user_profile,user_media
              &response_type=code
        """
        #  URL
        url = f'https://api.instagram.com/oauth/authorize?client_id={PROJECT_SERVICE_ID}&redirect_uri={redirect_uri}&scope=user_profile,user_media&response_type=code&state={state}'

        return requests.get(url)

    @classmethod
    def get_access_token(
            cls,
            code: str,
            redirect_uri: str = "https://staging-api.ozet.app/api/v1/member/user/me/instagram/oauth/authorize"
    ) -> Response:
        """
        Instagram Token Auth

        Args:

        Returns:
            response: Instagram API 응답

        Notes:
            curl -X POST \
              https://api.instagram.com/oauth/access_token \
              -F client_id=684477648739411 \
              -F client_secret=eb8c7... \
              -F grant_type=authorization_code \
              -F redirect_uri=https://socialsizzle.herokuapp.com/auth/ \
              -F code=AQDp3TtBQQ...
        """
        #  URL
        url = f'https://api.instagram.com/oauth/access_token'
        data = dict(
            client_id=PROJECT_SERVICE_ID,
            client_secret=SECRET_KEY,
            redirect_uri=redirect_uri,
            grant_type='authorization_code',
            code=code,
        )
        return requests.post(url, data)

    @classmethod
    def me(cls,
           access_token: str
    ):
        """
        Instagram Token Auth

        Args:

        Returns:
            response: Instagram API 응답

        Notes:
            GET https://graph.instagram.com/v12.0/me
              ?fields={fields}
              &access_token={access-token}
        """
        #  URL
        url = f'https://graph.instagram.com/{API_VERSION}/me?access_token={access_token}'

        return requests.get(url)

    @classmethod
    def media(
        cls,
        user_id: int,
        access_token: str,
    ):
        """
        Instagram Token Auth

        Args:

        Returns:
            response: Instagram API 응답

        Notes:
            GET https://graph.instagram.com/{api-version}/{user-id}/media
              ?access_token={access-token}
        """
        fields = 'id,media_type,media_url,timestamp'
        #  URL
        url = f'https://graph.instagram.com/{API_VERSION}/{user_id}/media?access_token={access_token}&field={fields}'

        return requests.get(url)
