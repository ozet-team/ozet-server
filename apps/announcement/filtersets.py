from apps.announcement.models import Announcement
from django_filters.rest_framework import FilterSet, filters


class AnnouncementFilterSet(FilterSet):
    employee_types = filters.BaseInFilter(
        field_name="employee_types__codename",
    )
    pay_types = filters.BaseInFilter(field_name="pay_type")

    class Meta:
        model = Announcement
        fields = ["employee_types", "pay_types"]
