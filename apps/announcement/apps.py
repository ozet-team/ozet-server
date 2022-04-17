from django.apps import AppConfig


class AnnouncementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.announcement"

    def ready(self):
        from .models import EmployeeType

        for codename, value in EmployeeType.Type.__members__.items():
            EmployeeType.objects.get_or_create(
                name=value.value,
                codename=codename,
            )
