from apps.member import views
from django.urls import path


urlpatterns = [
    path(
        "auth/passcode/request",
        views.UserPasscodeVertifyRequestView.as_view(),
        name=views.UserPasscodeVertifyRequestView.__name__,
    ),
    path(
        "auth/passcode",
        views.UserPasscodeVertifyView.as_view(),
        name=views.UserPasscodeVertifyView.__name__,
    ),
]
