from apps.announcement.models import Announcement
from rest_framework import serializers


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "shop_name",
            "manager_name",
            "manager_phone_number",
            "expired_datetime",
            "working_hour_start",
            "working_hour_end",
            "pay_type",
            "pay_amount",
            "employee_types",
            "description",
        ]
