from apps.announcement import views
from django.urls import path

app_name = "announcement"


urlpatterns = [
    path("announcements/", views.AnnouncementViewSet.as_view({"get": "list"})),
    path(
        "announcements/<int:pk>",
        views.AnnouncementViewSet.as_view({"get": "retrieve"}),
    ),
]
