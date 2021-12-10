from apps.member import views
from django.urls import path


urlpatterns = [
    path(
        "user/auth/passcode",
        views.UserPasscodeVeritfyView.as_view(),
        name=views.UserPasscodeVeritfyView.__name__,
    ),
    path(
        "user/auth/passcode/request",
        views.UserPasscodeVeritfyView.as_view(),
        name=views.UserPasscodeVeritfyRequestView.__name__,
    ),
]
