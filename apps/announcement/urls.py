from apps.announcement import views
from django.urls import path

app_name = "announcement"


urlpatterns = [
    path("announcements/", views.AnnouncementViewSet.as_view({"get": "list"})),
    path(
        "announcements/<int:pk>/",
        views.AnnouncementViewSet.as_view({"get": "retrieve"}),
    ),
    path("bookmarks/", views.BookmarkViewSet.as_view({"get": "list"})),
    path(
        "bookmarks/<int:pk>/",
        views.BookmarkViewSet.as_view({"post": "create", "delete": "destroy"}),
    ),
]
