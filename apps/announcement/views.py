from apps.announcement.filtersets import AnnouncementFilterSet
from apps.announcement.models import Announcement, Bookmark
from apps.announcement.serializers import AnnouncementSerializer, BookmarkSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class AnnouncementViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = AnnouncementSerializer
    queryset = AnnouncementSerializer.process_queryset(Announcement.objects.all())
    filterset_class = AnnouncementFilterSet
    pagination_class = LimitOffsetPagination


class BookmarkViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = BookmarkSerializer
    queryset = BookmarkSerializer.process_queryset(Bookmark.objects.all())
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
