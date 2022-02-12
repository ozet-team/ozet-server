from django.db import models


class City(models.Model):
    name = models.CharField(max_length=16, unique=True)


class Country(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="country_set")
    name = models.CharField(max_length=32)

    class Meta:
        unique_together = ("city", "name")
