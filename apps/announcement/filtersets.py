from apps.announcement.models import Announcement, Bookmark
from django_filters.rest_framework import FilterSet, filters


class AnnouncementFilterSet(FilterSet):
    employee_types = filters.BaseInFilter(
        field_name="employee_types__codename",
    )
    pay_types = filters.BaseInFilter(field_name="pay_type")
    city_id_list = filters.BaseInFilter(field_name="city_id")
    country_id_list = filters.BaseInFilter(field_name="country_id")

    class Meta:
        model = Announcement
        fields = ["employee_types", "pay_types", "city_id", "country_id_list"]


class BookmarkFilterSet(FilterSet):
    class Meta:
        model = Bookmark
        fields = ["user_id"]
