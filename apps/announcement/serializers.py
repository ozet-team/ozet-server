from django.db.models import Count

from apps.announcement.models import Announcement, Bookmark, EmployeeType
from rest_framework import serializers


class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = ["id", "name"]


class AnnouncementSerializer(serializers.ModelSerializer):
    employee_types = EmployeeTypeSerializer(many=True, default=[])
    bookmark_count = serializers.IntegerField()

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
            "bookmark_count",
            "image_url",
        ]

    @classmethod
    def process_queryset(cls, queryset):
        return queryset.prefetch_related("employee_types").annotate(
            bookmark_count=Count("bookmark_set")
        )


class BookmarkSerializer(serializers.ModelSerializer):
    announcement = AnnouncementSerializer(read_only=True)
    announcement_id = serializers.PrimaryKeyRelatedField(
        source="announcement",
        write_only=True,
        queryset=Announcement.objects.all(),
    )

    class Meta:
        model = Bookmark
        fields = [
            "id",
            "announcement",
            "announcement_id",
        ]

    @classmethod
    def process_queryset(cls, queryset):
        return queryset.select_related("user", "announcement").prefetch_related(
            "announcement__employee_types"
        )
