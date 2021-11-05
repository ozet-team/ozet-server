# -*- coding: utf-8 -*-

from django.db.models import Prefetch, Model
from django.db.models.base import ModelBase

from .manager import cf_orm_manager


class CacheFrameworkPrefetch(Prefetch):

    def __init__(self, lookup, queryset, to_attr=None):
        super(CacheFrameworkPrefetch, self).__init__(lookup, queryset=queryset, to_attr=to_attr)
        if '__' in lookup:
            raise ValueError(f'{self.__class__.__name__} does not support nested relationship.')


class CacheFrameworkPrefetchDescriptor(object):

    def __init__(self, func, prefetch, name=None):
        self.func = func
        self.prefetch = prefetch
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, cls=None):
        """
        Call the function and put the return value in instance.__dict__ so that
        subsequent attribute access on the instance returns the cached value
        instead of calling cached_property.__get__().
        """
        if instance is None:
            return self.prefetch
        return self.func(instance)


def _make_cf_prefetch_property(field_name, prefetch):
    def get_queryset(self):
        if hasattr(self, prefetch.to_attr):
            return getattr(self, prefetch.to_attr, None)

        prefetch_through = prefetch.prefetch_through

        # noinspection PyProtectedMember
        meta = self._meta
        fk_fields = {f.name: f for f in meta.local_fields if f.remote_field}
        m2m_fields = {f.name: f for f in meta.local_many_to_many}

        if prefetch_through in fk_fields:
            fk_field = fk_fields[prefetch_through]
            pk = fk_field.value_from_object(self)
            if not pk:
                return

            # noinspection PyProtectedMember
            pk_field = fk_field.remote_field.model._meta.pk.name
            rv = prefetch.queryset.filter(**{pk_field: pk}).first()
            setattr(self, prefetch.to_attr, rv)
            return rv

        if prefetch_through in m2m_fields:
            qs = getattr(self, prefetch_through, None).all() & prefetch.queryset
            rv = list(qs)
            setattr(self, prefetch.to_attr, rv)
            return rv
        raise ValueError(f'Could not find any relationship for {field_name}.')
    return CacheFrameworkPrefetchDescriptor(get_queryset, prefetch=prefetch, name=field_name)


class CacheFrameworkModelBase(ModelBase):

    # noinspection PyMethodParameters
    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)

        # CacheFramework prefetch fields
        cf_prefetch_fields = {}
        for field_name, field in new_class.__dict__.items():
            if isinstance(field, CacheFrameworkPrefetch):
                field = CacheFrameworkPrefetch(lookup=field.prefetch_through,
                                               queryset=field.queryset,
                                               to_attr=f'_{field_name}')
                cf_prefetch_fields[field_name] = field
                p = _make_cf_prefetch_property(field_name, field)
                setattr(new_class, field_name, p)

        # noinspection PyProtectedMember
        new_class._meta.local_cf_prefetch_fields = cf_prefetch_fields
        return new_class


class CacheFrameworkModel(Model, metaclass=CacheFrameworkModelBase):
    cf_expire = 60 * 60 * 24

    class Meta:
        abstract = True

    def create_cache(self):
        cf_orm_manager.create(self)

    def delete_cache(self):
        cf_orm_manager.delete(self.__class__, self.id)

    def save(self, *args, **kwargs):
        rv = super(CacheFrameworkModel, self).save(*args, **kwargs)
        self.create_cache()
        return rv

    def delete(self, *args, **kwargs):
        self.delete_cache()
        return super(CacheFrameworkModel, self).delete(*args, **kwargs)

    @classmethod
    def cf_queryset(cls):
        return cls.objects.all()

    @classmethod
    def get_cached(cls, pk, prefetch_fields=None, auto_create=True):
        return cf_orm_manager.get(cls, pk, prefetch_fields=prefetch_fields, auto_create=auto_create)

    @classmethod
    def get_many_cached(cls, pk_list, prefetch_fields=None, auto_create=True):
        return cf_orm_manager.get_many(cls, pk_list, prefetch_fields=prefetch_fields, auto_create=auto_create)
