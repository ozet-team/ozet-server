from django.conf import settings

from apps.member import views
from django.urls import path


urlpatterns = [
    path(
        "auth/passcode/request",
        views.UserPasscodeVerifyRequestView.as_view(),
        name=views.UserPasscodeVerifyRequestView.__name__,
    ),
    path(
        "auth/passcode/",
        views.UserPasscodeVerifyView.as_view(),
        name=views.UserPasscodeVerifyView.__name__,
    ),
    path(
        "user/me/",
        views.UserMeView.as_view(),
        name=views.UserMeView.__name__,
    ),
    path(
        "user/<int:id>/",
        views.UserDetailView.as_view(),
        name=views.UserDetailView.__name__,
    ),
    path(
        "user/me/instagram/oauth/authorize/",
        views.UserInstagramOAuthView.as_view(),
        name=views.UserInstagramOAuthView.__name__,
    ),
    path(
        "user/me/instagram/oauth/cancel/",
        views.UserInstagramOAuthCancelView.as_view(),
        name=views.UserInstagramOAuthCancelView.__name__,
    ),
    path(
        "user/me/instagram/oauth/delete/",
        views.UserInstagramOAuthDeleteView.as_view(),
        name=views.UserInstagramOAuthDeleteView.__name__,
    ),
]

if settings.DEBUG:
    debug_urlpatterns = [
        path(
            "auth/passcode/pass/",
            views.UserPasscodeVerifyPassView.as_view(),
            name=views.UserPasscodeVerifyPassView.__name__,
        ),
        path(
            "auth/login/",
            views.UserTokenLoginView.as_view(),
            name=views.UserTokenLoginView.__name__,
        ),
        path(
            "auth/token/refresh/",
            views.UserTokenRefreshView.as_view(),
            name=views.UserTokenRefreshView.__name__,
        ),
    ]

    urlpatterns += debug_urlpatterns
