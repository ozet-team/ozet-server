from django.conf import settings

from apps.resume import views
from django.urls import path


urlpatterns = [
    path(
        "user/resume",
        views.UserResumeDetailView.as_view(),
        name=views.UserResumeDetailView.__name__,
    ),
]

if settings.DEBUG:
    debug_urlpatterns = [
        path(
            "resume/<str:code>",
            views.ResumeDetailView.as_view(),
            name=views.ResumeDetailView.__name__,
        ),
    ]

    urlpatterns.append(*debug_urlpatterns)
