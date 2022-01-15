from apps.announcement.filtersets import AnnouncementFilterSet
from apps.announcement.models import Announcement
from apps.announcement.serializers import AnnouncementSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ReadOnlyModelViewSet


class AnnouncementViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()
    filterset_class = AnnouncementFilterSet
    pagination_class = LimitOffsetPagination
