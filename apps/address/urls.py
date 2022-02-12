from apps.address import views
from django.urls import path

app_name = "address"


urlpatterns = [
    path("cities/", views.CityListAPIView.as_view()),
    path(
        "countries/",
        views.CountryListAPIView.as_view(),
    ),
]
