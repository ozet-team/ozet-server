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
            "shop_location",
            "manager_name",
            "manager_phone_number",
            "expire_type",
            "expired_datetime",
            "working_hour",
            "pay_type",
            "pay_amount",
            "employee_types",
            "description",
        ]
