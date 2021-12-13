from django.conf import settings

from apps.resume import views
from django.urls import path


urlpatterns = [
    path(
        "user/me/resume",
        views.ResumeDetailView.as_view(),
        name=views.ResumeDetailView.__name__,
    ),
    path(
        "user/me/resume/career",
        views.ResumeCareerListView.as_view(),
        name=views.ResumeCareerListView.__name__,
    ),
    path(
        "user/me/resume/career/<int:id>",
        views.ResumeCareerDetailView.as_view(),
        name=views.ResumeCareerDetailView.__name__,
    ),
    path(
        "user/me/resume/certificate",
        views.ResumeCertificateListView.as_view(),
        name=views.ResumeCertificateListView.__name__,
    ),
    path(
        "user/me/resume/certificate/<int:id>",
        views.ResumeCertificateDetailView.as_view(),
        name=views.ResumeCertificateDetailView.__name__,
    ),
    path(
        "user/me/resume/academic",
        views.ResumeAcademicBackgroundListView.as_view(),
        name=views.ResumeAcademicBackgroundListView.__name__,
    ),
    path(
        "user/me/resume/academic/<int:id>",
        views.ResumeAcademicBackgroundDetailView.as_view(),
        name=views.ResumeAcademicBackgroundDetailView.__name__,
    ),
    path(
        "user/me/resume/military",
        views.ResumeMilitaryServiceView.as_view(),
        name=views.ResumeMilitaryServiceView.__name__,
    ),
]