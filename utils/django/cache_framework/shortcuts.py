# -*- coding: utf-8 -*-
from django.http import Http404


def get_cached_or_404(model_cls, pk, prefetch_fields=None):
    from .models import CacheFrameworkModel

    if not issubclass(model_cls, CacheFrameworkModel):
        raise ValueError("First argument to get_cached_or_404() must be a subclass of CacheFrameworkModel")

    obj = model_cls.get_cached(pk, prefetch_fields=prefetch_fields)
    if not obj:
        raise Http404
    return obj
