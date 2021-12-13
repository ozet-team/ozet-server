from django.conf import settings

from apps.resume import views
from django.urls import path


urlpatterns = [
    path(
        "user/resume/<str:code>",
        views.UserResumeDetailView.as_view(),
        name=views.UserResumeDetailView.__name__,
    ),
    path(
        "user/resume",
        views.UserResumeListView.as_view(),
        name=views.UserResumeListView.__name__,
    ),
]

if settings.DEBUG:
    debug_urlpatterns = [
        path(
            "user/resume/<str:code>/pass",
            views.ResumeDetailView.as_view(),
            name=views.ResumeDetailView.__name__,
        ),
    ]

    urlpatterns.append(*debug_urlpatterns)
