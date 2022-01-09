from apps.announcement.models import Announcement, EmployeeType
from django_filters.rest_framework import FilterSet, filters


class AnnouncementFilterSet(FilterSet):
    employee_type = filters.ChoiceFilter(
        field_name="employee_types__codename",
        lookup_expr="in",
        choices=list(EmployeeType.Type.__members__.items()),
    )
    pay_type = filters.ChoiceFilter(choices=Announcement.PayType)

    class Meta:
        model = Announcement
        fields = ["employee_type"]
