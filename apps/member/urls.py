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
        "me",
        views.UserProfileView.as_view(),
        name=views.UserProfileView.__name__,
    ),
    path(
        "me/profile",
        views.UserProfileView.as_view(),
        name=views.UserProfileView.__name__,
    ),
]