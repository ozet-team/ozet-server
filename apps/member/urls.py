from apps.member import views
from django.urls import path


urlpatterns = [
    path(
        "user/auth/passcode",
        views.UserPasscodeVertifyView.as_view(),
        name=views.UserPasscodeVertifyView.__name__,
    ),
    path(
        "user/auth/passcode/request",
        views.UserPasscodeVertifyView.as_view(),
        name=views.UserPasscodeVertifyRequestView.__name__,
    ),
]
