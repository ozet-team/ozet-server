# -*- coding: utf-8 -*-
from django.db.models import QuerySet
from rest_framework.generics import ListAPIView, RetrieveAPIView

from utils.django.rest_framework.mixins import PersonalizedListMixin
from .models import CacheFrameworkModel
from .shortcuts import get_cached_or_404


class CacheFrameworkListAPIView(PersonalizedListMixin, ListAPIView):
    cf_model_class = None
    cf_pk_field = 'id'
    cf_prefetch_fields = None

    def filter_queryset(self, queryset):
        queryset = super(CacheFrameworkListAPIView, self).filter_queryset(queryset)
        if isinstance(queryset, QuerySet) and self.cf_pk_field:
            return queryset.values_list(self.cf_pk_field, flat=True).all()
        return queryset

    def get_personalized_list(self, iterator):
        return self.cf_model_class.get_many_cached(iterator, prefetch_fields=self.cf_prefetch_fields)


class CacheFrameworkRetrieveAPIView(RetrieveAPIView):
    cf_model_class = None
    cf_prefetch_fields = None

    def get_object(self):
        assert issubclass(self.cf_model_class, CacheFrameworkModel), (
            f'Expected cf_model_class {self.cf_model_class} to be subclass of CacheFrameworkModel'
        )

        assert self.lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, self.lookup_url_kwarg)
        )

        pk = self.kwargs[self.lookup_url_kwarg]
        obj = get_cached_or_404(self.cf_model_class, pk, prefetch_fields=self.cf_prefetch_fields)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
