from apps.address.constants import AppConstants
from apps.address.models import City, Country
from django.core.management import BaseCommand


class Command(BaseCommand):
    cities = list(AppConstants.ADDRESS.keys())

    def handle(self, *args, **options):
        for city_name in self.cities:
            city, _ = City.objects.get_or_create(name=city_name)

            for country_name in self.get_countries(city_name):
                Country.objects.get_or_create(city=city, name=country_name)

    def get_countries(self, city_name: str) -> list[str]:
        return AppConstants.ADDRESS[city_name]
