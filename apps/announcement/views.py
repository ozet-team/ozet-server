from apps.announcement.models import Announcement
from apps.announcement.serializers import AnnouncementSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet


class AnnouncementViewSet(ReadOnlyModelViewSet):
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()
