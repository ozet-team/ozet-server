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
        "auth/passcode",
        views.UserPasscodeVerifyView.as_view(),
        name=views.UserPasscodeVerifyView.__name__,
    ),
    path(
        "user/me",
        views.UserMeView.as_view(),
        name=views.UserMeView.__name__,
    ),
]

if settings.DEBUG:
    debug_urlpatterns = [
        path(
            "auth/passcode/pass",
            views.UserPasscodeVerifyPassView.as_view(),
            name=views.UserPasscodeVerifyPassView.__name__,
        ),
    ]

    urlpatterns.append(*debug_urlpatterns)
