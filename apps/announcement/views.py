from apps.announcement.models import Announcement
from apps.announcement.serializers import AnnouncementSerializer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


def fake_response(i: int):
    return {
        "id": i,
        "title": f"테스트 공고 {i}",
        "shop_name": f"겁나 잘자르는 분쇄헤어 {i}",
        "manager_name": "박분쇄",
        "manager_phone_number": f"010-{i:04}-{i:04}",
        "expired_datetime": "2022-03-01",
        "working_hour_start": 1,
        "working_hour_end": 23,
        "pay_type": Announcement.PayType.values[0],
        "pay_amount": 100_000,
        "employee_types": ["디자이너", "인턴"],
        "description": None,
    }


class AnnouncementViewSet(ModelViewSet):
    serializer_class = AnnouncementSerializer
    queryset = ""

    def list(self, request, *args, **kwargs):
        return Response([fake_response(i) for i in range(10)])

    def retrieve(self, request, *args, **kwargs):
        return Response(fake_response(kwargs["pk"]))
