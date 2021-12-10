from apps.announcement.models import Announcement, EmployeeType
from rest_framework import serializers


class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = ["id", "name"]


class AnnouncementSerializer(serializers.ModelSerializer):
    employee_types = EmployeeTypeSerializer(many=True, default=[])

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
