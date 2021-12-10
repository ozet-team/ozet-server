from apps.announcement.models import Announcement
from apps.announcement.serializers import AnnouncementSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class AnnouncementViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()
