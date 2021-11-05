# -*- coding: utf-8 -*-
from django.urls import path

from . import views

urlpatterns = [
    path('auth/facebook/',
         views.FacebookLoginAPIView.as_view(),
         name=views.FacebookLoginAPIView.__name__),
    path('auth/kakao/',
         views.KakaoLoginAPIView.as_view(),
         name=views.KakaoLoginAPIView.__name__),
    path('auth/naver/',
         views.NaverLoginAPIView.as_view(),
         name=views.NaverLoginAPIView.__name__),
    path('auth/google/',
         views.GoogleLoginAPIView.as_view(),
         name=views.GoogleLoginAPIView.__name__),
    path('auth/apple/',
         views.AppleLoginAPIView.as_view(),
         name=views.AppleLoginAPIView.__name__),
    path('auth/test/',
         views.TestLoginAPIView.as_view(),
         name=views.TestLoginAPIView.__name__),
    path('auth/username/',
         views.UsernameLoginAPIView.as_view(),
         name=views.UsernameLoginAPIView.__name__),
    path('logout/',
         views.LogoutAPIView.as_view(),
         name=views.LogoutAPIView.__name__),
]
