from apps.address.models import City, Country
from apps.address.serializers import CitySerializer, CountrySerializer
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CityListAPIView(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CitySerializer
    queryset = City.objects.all()


class CountryListAPIView(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
    filterset_fields = ["city_id"]
