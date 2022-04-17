import re
import json
from typing import Union, Literal, Optional, Tuple, Any

from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from django.conf import settings
import requests

from requests import Response

PROJECT_SERVICE_ID = "658909912196679"
PROJECT_SERVICE_NAME = "ozet"
SECRET_KEY = "9421262ee369d46bb82c372db0bf3c8e"
API_VERSION = "v12.0"

REDIRECT_URL = getattr(
    settings,
    "INSTAGRAM_OAUTH_REDIRECT_URL",
    "https://staging-api.ozet.app/api/v1/member/user/me/instagram/oauth/authorize"
)

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
            redirect_uri: str = REDIRECT_URL
    ) -> Optional[str]:
        """
        Instagram OAuth

        Args:

        Returns:
            response: Instagram API 응답 - OAuth 인증 페이지 URI

        Notes:
            https://api.instagram.com/oauth/authorize
              ?client_id={app-id}
              &redirect_uri={redirect-uri}
              &scope=user_profile,user_media
              &response_type=code
        """
        query_params=f'client_id={PROJECT_SERVICE_ID}&redirect_uri={redirect_uri}&scope=user_profile,user_media&response_type=code&state={state}'

        url = f'https://api.instagram.com/oauth/authorize?{query_params}'

        try:
            res = requests.get(url)
        except requests.exceptions.RequestException as e:
            return None

        return res.url

    @classmethod
    def get_access_token(
            cls,
            code: str,
            redirect_uri: str = REDIRECT_URL
    ) -> tuple[Any, Any]:
        """
        Instagram Access Token Auth

        Args:

        Returns:
            {
              "access_token": "IGQVJ...",
              "user_id": 17841405793187218
            }

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
        try:
            res = requests.post(url, data)
        except requests.exceptions.RequestException as e:
            return None, None


        content = json.loads(res.content)

        return content.get("access_token", None), content.get("user_id", None)

    @classmethod
    def get_extend_access_token(
            cls,
            access_token: str,
    ) -> tuple[Any, Any, Any]:
        """
        Instagram Exchange Access Token To Extend Access Token

        Args:

        Returns:
            {
              "access_token":"{long-lived-user-access-token}",
              "token_type": "bearer",
              "expires_in": 5183944  // Number of seconds until token expires
            }

        Notes:
            curl -i -X GET "https://graph.instagram.com/access_token
              ?grant_type=ig_exchange_token
              &client_secret={instagram-app-secret}
              &access_token={short-lived-access-token}"
        """
        query_params = f'grant_type=ig_exchange_token&client_secret={SECRET_KEY}&access_token={access_token}'

        url = f'https://graph.instagram.com/access_token?{query_params}'

        try:
            res = requests.get(url)
        except requests.exceptions.RequestException as e:
            return None, None, None

        content = json.loads(res.content)

        return content.get("access_token", None), content.get("token_type", None), content.get("expires_in", None)

    @classmethod
    def refresh_extend_access_token(
            cls,
            access_token: str,
    ) -> Response:
        """
        Instagram Refresh Extend Access Token

        Args:

        Returns:
            {
              "access_token":"{long-lived-user-access-token}",
              "token_type": "bearer",
              "expires_in": 5183944 // Number of seconds until token expires
            }

        Notes:
            curl -i -X GET "https://graph.instagram.com/refresh_access_token
              ?grant_type=ig_refresh_token
              &access_token={long-lived-access-token}"
        """
        query_params = f'grant_type=ig_refresh_token&access_token={access_token}'

        url = f'https://api.instagram.com/oauth/refresh_access_token?{query_params}'

        return requests.get(url)

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
        fields = 'id,username'
        query_params = f'access_token={access_token}&fields={fields}'

        url = f'https://graph.instagram.com/{API_VERSION}/me?{query_params}'

        try:
            res = requests.get(url)
        except requests.exceptions.RequestException as e:
            return None

        content = json.loads(res.content)

        return content


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
        query_params = f'access_token={access_token}&fields={fields}'

        url = f'https://graph.instagram.com/{API_VERSION}/{user_id}/media?{query_params}'

        try:
            res = requests.get(url)
        except requests.exceptions.RequestException as e:
            return None

        content = json.loads(res.content)

        return content
