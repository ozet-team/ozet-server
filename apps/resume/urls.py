from django.conf import settings

from apps.resume import views
from django.urls import path


urlpatterns = [
    path(
        "user/me/resume",
        views.UserResumeDetailView.as_view(),
        name=views.UserResumeDetailView.__name__,
    ),
]