# -*- coding: utf-8 -*-
import json

# noinspection PyProtectedMember
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.serializers import serialize, deserialize
from django_redis import get_redis_connection

# noinspection PyUnresolvedReferences
from . import serializer


def get_remote_fields(model_cls):
    from .models import CacheFrameworkModel

    fields = dict()

    # noinspection PyProtectedMember
    meta = model_cls._meta
    for field in meta.local_fields:
        if not field.remote_field:
            continue

        field_name = field.name
        field = getattr(model_cls, field.name).field
        field_model_cls = field.related_model
        field_attr = field.get_attname()
        fields[field_name] = dict(model_cls=field_model_cls,
                                  pk_field=field_attr,
                                  is_cacheable=issubclass(field_model_cls, CacheFrameworkModel))
    return fields


def get_m2m_fields(model_cls):
    from .models import CacheFrameworkModel

    fields = dict()

    # noinspection PyProtectedMember
    meta = model_cls._meta
    for field in meta.local_many_to_many:
        field_name = field.name
        field_model_cls = field.remote_field.model
        fields[field_name] = dict(model_cls=field_model_cls,
                                  is_cacheable=issubclass(field_model_cls, CacheFrameworkModel))
    return fields


def get_cf_prefetch_fields(model_cls):
    from .models import CacheFrameworkModel

    # noinspection PyProtectedMember
    meta = model_cls._meta

    fields = dict()
    fk_fields = {f.name: f for f in meta.local_fields if f.remote_field}
    m2m_fields = {f.name: f for f in meta.local_many_to_many}

    for field_name, prefetch in getattr(meta, 'local_cf_prefetch_fields', {}).items():
        fk_field = fk_fields.get(prefetch.prefetch_through)
        m2m_field = m2m_fields.get(prefetch.prefetch_through)
        if fk_field:
            field_type = 'fk'
            field = fk_field
        elif m2m_field:
            field_type = 'm2m'
            field = m2m_field
        else:
            continue

        field_model_cls = field.remote_field.model
        fields[field_name] = dict(model_cls=field_model_cls,
                                  type=field_type,
                                  prefetch=prefetch,
                                  is_cacheable=issubclass(field_model_cls, CacheFrameworkModel))
    return fields


def parse_prefetch_fields(prefetch_fields):
    if not prefetch_fields:
        return {}

    fields = {}
    for field in prefetch_fields:
        if '__' in field:
            continue
        fields[field] = []

    for field in prefetch_fields:
        if '__' not in field:
            continue
        separated_names = field.split('__')
        if not separated_names:
            continue
        target_field = separated_names[0]
        related_field = '__'.join(separated_names[1:])
        if target_field not in fields or related_field in fields[target_field]:
            continue
        fields[target_field].append(related_field)
    return fields


class BaseManager(object):
    key_prefix = None

    cache_alias = DEFAULT_CACHE_ALIAS

    def serialize(self, obj):
        raise NotImplementedError()

    def deserialize(self, cached):
        raise NotImplementedError()

    def make_key(self, key):
        if not self.key_prefix:
            return key
        return f'{self.key_prefix}:{key}'


class CacheFrameworkOrmManager(BaseManager):
    key_prefix = 'models'

    serializer_engine = 'cache_framework'

    def __init__(self, serializer_engine=None):
        self.serializer_engine = serializer_engine or self.serializer_engine

    def serialize(self, obj):
        return serialize(self.serializer_engine, [obj])

    def deserialize(self, cached):
        deserialize_object = list(deserialize(self.serializer_engine, cached))
        if not deserialize_object:
            return None
        return deserialize_object[0]

    def make_model_key(self, model_cls, pk):
        # noinspection PyProtectedMember
        meta = model_cls._meta
        key = f'{meta.db_table}:{pk}'
        return self.make_key(key)

    def get(self, model_cls, pk, prefetch_fields=None, auto_create=True):
        from .models import CacheFrameworkModel

        if not issubclass(model_cls, CacheFrameworkModel):
            return None

        key = self.make_model_key(model_cls, pk)
        rv = caches[self.cache_alias].get(key)

        if rv:
            deserialize_object = self.deserialize(rv)
            if deserialize_object:
                prefetch_fields = parse_prefetch_fields(prefetch_fields)
                if prefetch_fields:
                    self.handle_remote_fields(model_cls, [deserialize_object], prefetch_fields)
                    self.handle_m2m_fields(model_cls, [deserialize_object], prefetch_fields)
                    self.handle_cf_prefetch_fields(model_cls, [deserialize_object], prefetch_fields)
                return deserialize_object.object

            # 비정상 캐시 삭제
            self.delete(model_cls, pk)

        if not auto_create:
            return None

        obj = model_cls.cf_queryset().filter(pk=pk).first()
        if not obj:
            return None

        self.create(obj)
        return self.get(model_cls, pk, auto_create=False)

    def get_many(self, model_cls, pk_list, prefetch_fields=None, auto_create=True):
        keys = {pk: self.make_model_key(model_cls, pk) for pk in pk_list}

        if not keys:
            return []

        rv = caches[self.cache_alias].get_many(keys.values())
        cached_objects = {}
        for k, v in rv.items():
            deserialize_object = self.deserialize(v)
            if deserialize_object:
                cached_objects[k] = deserialize_object
                continue

            # 비정상 캐시 삭제
            caches[self.cache_alias].delete(k)
        cached_keys = cached_objects.keys()

        non_cached_keys = {pk: key for pk, key in keys.items() if key not in cached_keys}
        non_cached_pk_list = non_cached_keys.keys()

        if not non_cached_pk_list or not auto_create:
            prefetch_fields = parse_prefetch_fields(prefetch_fields)
            if prefetch_fields:
                deserialized_objects = cached_objects.values()
                self.handle_remote_fields(model_cls, deserialized_objects, prefetch_fields)
                self.handle_m2m_fields(model_cls, deserialized_objects, prefetch_fields)
                self.handle_cf_prefetch_fields(model_cls, deserialized_objects, prefetch_fields)

            objects = []
            for pk in pk_list:
                key = keys.get(pk)
                if not key:
                    continue
                deserialize_object = cached_objects.get(key)
                if not deserialize_object:
                    continue
                objects.append(deserialize_object.object)
            return objects

        non_cached_objects = model_cls.cf_queryset().filter(pk__in=non_cached_pk_list).all()
        for obj in non_cached_objects:
            self.create(obj)
        return self.get_many(model_cls, pk_list, auto_create=False)

    def has_cache(self, model_cls, pk):
        key = self.make_model_key(model_cls, pk)
        return caches[self.cache_alias].get(key) is not None

    def create(self, obj):
        from .models import CacheFrameworkModel

        model_cls = obj.__class__
        if not issubclass(model_cls, CacheFrameworkModel):
            return False

        # noinspection PyProtectedMember
        pk = getattr(obj, model_cls._meta.pk.name)
        key = self.make_model_key(model_cls, pk)
        serialized = self.serialize(obj)
        caches[self.cache_alias].set(key, serialized, model_cls.cf_expire)
        return True

    def delete(self, model_cls, pk):
        key = self.make_model_key(model_cls, pk)
        caches[self.cache_alias].delete(key)

    def handle_remote_fields(self, model_cls, deserialized_objects, prefetch_fields):

        # make fields
        tmp_remote_fields = get_remote_fields(model_cls=model_cls)
        remote_fields = {}
        for field_name, field in tmp_remote_fields.items():
            nested_prefetch_fields = prefetch_fields.get(field_name)
            if nested_prefetch_fields is None:
                continue

            field['nested_prefetch_fields'] = nested_prefetch_fields
            field['pk_list'] = []
            remote_fields[field_name] = field

        # getting pk
        for deserialized_object in deserialized_objects:
            obj = deserialized_object.object
            for field_name, field in remote_fields.items():
                pk = getattr(obj, field['pk_field'])
                if pk:
                    remote_fields[field_name]['pk_list'].append(pk)

        # getting objects
        remote_objects = {}
        for field_name, field in remote_fields.items():
            remote_objects[field_name] = {}
            pk_list = list(set(field.get('pk_list', [])))
            if not pk_list:
                continue

            remote_model_cls = field['model_cls']
            nested_prefetch_fields = field['nested_prefetch_fields']
            is_cacheable = field['is_cacheable']
            if is_cacheable:
                objects = self.get_many(remote_model_cls, pk_list, prefetch_fields=nested_prefetch_fields)
            else:
                qs = remote_model_cls.objects.filter(pk__in=pk_list)
                if nested_prefetch_fields:
                    qs = qs.prefetch_related(*nested_prefetch_fields)
                objects = qs.all()

            for obj in objects:
                remote_objects[field_name][obj.pk] = obj

        # set objects
        for deserialized_object in deserialized_objects:
            obj = deserialized_object.object
            for field_name, field in remote_fields.items():
                if field_name not in remote_objects:
                    continue

                pk = getattr(obj, field['pk_field'])
                if not pk:
                    continue

                remote_object = remote_objects[field_name].get(pk)
                if not remote_object:
                    continue

                # noinspection PyProtectedMember
                obj._state.fields_cache[field_name] = remote_object

    def handle_m2m_fields(self, model_cls, deserialized_objects, prefetch_fields):

        # make fields
        tmp_m2m_fields = get_m2m_fields(model_cls=model_cls)
        m2m_fields = {}
        for field_name, field in tmp_m2m_fields.items():
            nested_prefetch_fields = prefetch_fields.get(field_name)
            if nested_prefetch_fields is None:
                continue

            field['nested_prefetch_fields'] = nested_prefetch_fields
            field['pk_list'] = []
            m2m_fields[field_name] = field

        # getting pk_list
        for deserialized_object in deserialized_objects:
            m2m_data = deserialized_object.m2m_data
            for field_name, field in m2m_fields.items():
                pk_list = m2m_data.get(field_name)
                if not pk_list:
                    continue
                m2m_fields[field_name]['pk_list'] += pk_list

        # getting objects
        m2m_objects = {}
        for field_name, field in m2m_fields.items():
            m2m_objects[field_name] = {}
            pk_list = list(set(field.get('pk_list', [])))
            if not pk_list:
                continue

            field_model_cls = field['model_cls']
            nested_prefetch_fields = field['nested_prefetch_fields']
            is_cacheable = field['is_cacheable']
            if is_cacheable:
                objects = self.get_many(field_model_cls, pk_list, prefetch_fields=nested_prefetch_fields)
            else:
                qs = field_model_cls.objects.filter(pk__in=pk_list)
                if nested_prefetch_fields:
                    qs = qs.prefetch_related(*nested_prefetch_fields)
                objects = qs.all()

            for obj in objects:
                m2m_objects[field_name][obj.pk] = obj

        # set objects
        for deserialized_object in deserialized_objects:
            obj = deserialized_object.object
            m2m_data = deserialized_object.m2m_data
            if not hasattr(obj, '_prefetched_objects_cache'):
                obj._prefetched_objects_cache = {}

            for field_name, field in m2m_fields.items():
                if field_name not in m2m_objects:
                    continue

                pk_list = m2m_data.get(field_name)
                if pk_list is None:
                    continue

                field_model_cls = field['model_cls']
                result_cache = [m2m_objects[field_name][pk]
                                for pk in pk_list if pk in m2m_objects[field_name]]
                m2m_qs = field_model_cls.objects.all()
                m2m_qs._result_cache = result_cache
                obj._prefetched_objects_cache[field_name] = m2m_qs

    def handle_cf_prefetch_fields(self, model_cls, deserialized_objects, prefetch_fields):
        # make fields
        tmp_cf_prefetch_fields = get_cf_prefetch_fields(model_cls=model_cls)
        cf_prefetch_fields = {}
        for field_name, field in tmp_cf_prefetch_fields.items():
            nested_prefetch_fields = prefetch_fields.get(field_name)
            if nested_prefetch_fields is None:
                continue

            field['nested_prefetch_fields'] = nested_prefetch_fields
            field['pk_list'] = []
            cf_prefetch_fields[field_name] = field

        # getting pk_list
        for deserialized_object in deserialized_objects:
            prefetch_data = deserialized_object.prefetch_data
            for field_name, field in cf_prefetch_fields.items():
                field_type = field['type']
                if field_type == 'fk':
                    pk = prefetch_data.get(field_name)
                    if not pk:
                        continue
                    cf_prefetch_fields[field_name]['pk_list'].append(pk)
                elif field_type == 'm2m':
                    pk_list = prefetch_data.get(field_name)
                    if not pk_list:
                        continue
                    cf_prefetch_fields[field_name]['pk_list'] += pk_list

        # getting objects
        cf_prefetch_objects = {}
        for field_name, field in cf_prefetch_fields.items():
            cf_prefetch_objects[field_name] = {}
            pk_list = list(set(field.get('pk_list', [])))
            if not pk_list:
                continue

            field_model_cls = field['model_cls']
            prefetch = field['prefetch']
            nested_prefetch_fields = field['nested_prefetch_fields']
            is_cacheable = field['is_cacheable']
            if is_cacheable:
                objects = self.get_many(field_model_cls, pk_list, prefetch_fields=nested_prefetch_fields)
            else:
                qs = prefetch.queryset.filter(pk__in=pk_list)
                if nested_prefetch_fields:
                    qs = qs.prefetch_related(*nested_prefetch_fields)
                objects = qs.all()

            for obj in objects:
                cf_prefetch_objects[field_name][obj.pk] = obj

        # set objects
        for deserialized_object in deserialized_objects:
            obj = deserialized_object.object
            prefetch_data = deserialized_object.prefetch_data

            for field_name, field in cf_prefetch_fields.items():
                if field_name not in cf_prefetch_objects:
                    continue

                field_type = field['type']
                if field_type == 'fk':
                    pk = prefetch_data.get(field_name)
                    if not pk or pk not in cf_prefetch_objects[field_name]:
                        continue
                    rv = cf_prefetch_objects[field_name][pk]
                elif field_type == 'm2m':
                    pk_list = prefetch_data.get(field_name)
                    if pk_list is None:
                        continue
                    rv = [cf_prefetch_objects[field_name][pk]
                          for pk in pk_list if pk in cf_prefetch_objects[field_name]]
                else:
                    continue
                prefetch = field['prefetch']
                setattr(obj, prefetch.to_attr, rv)


class CacheFrameworkSimpleManager(BaseManager):
    key_prefix = 'simple'

    def serialize(self, obj):
        return json.dumps(obj)

    def deserialize(self, cached):
        return json.loads(cached)

    def get(self, key):
        key = self.make_key(key)
        cached = caches[self.cache_alias].get(key)
        if not cached:
            return cached
        return self.deserialize(cached)

    def get_many(self, keys):
        raw_keys = {self.make_key(key): key for key in keys}
        rv = caches[self.cache_alias].get_many(list(raw_keys.keys()))
        items = {}
        for raw_key, value in rv.items():
            if not value:
                continue
            value = self.deserialize(value)
            key = raw_keys[raw_key]
            items[key] = value
        return items

    def create_many(self, data, expire=DEFAULT_TIMEOUT):
        data = {
            self.make_key(k): self.serialize(v)
            for k, v in data.items()
        }
        caches[self.cache_alias].set_many(data, expire)

    def create(self, key, value, expire=DEFAULT_TIMEOUT):
        key = self.make_key(key)
        cached = self.serialize(value)
        caches[self.cache_alias].set(key, cached, expire)

    def delete(self, key):
        key = self.make_key(key)
        caches[self.cache_alias].delete(key)

    def delete_pattern(self, pattern):
        pattern = self.make_key(pattern)
        caches[self.cache_alias].delete_pattern(pattern)

    def lock(self, key, timeout=10):
        key = f'lock:{key}'
        return caches[self.cache_alias].lock(key, timeout=timeout, blocking_timeout=timeout)

    def keys(self, key_prefix):
        key = self.make_key(key_prefix)
        raw_keys = caches[self.cache_alias].keys(f'{key}:*')
        keys = []
        for raw_key in raw_keys:
            key = ''.join(raw_key.split(key_prefix)[1:])
            key = f'{key_prefix}{key}'
            keys.append(key)
        return keys

    def sadd(self, key, *values):
        key = caches[self.cache_alias].make_key(self.make_key(key))
        client = get_redis_connection()
        client.sadd(key, *values)

    def sadd_with_expire(self, key, *values, expire=DEFAULT_TIMEOUT):
        key = caches[self.cache_alias].make_key(self.make_key(key))
        client = get_redis_connection()
        with client.pipeline() as pipe:
            pipe.sadd(key, *values)
            pipe.expire(key, expire)
            pipe.execute()

    def srem(self, key, *values):
        key = caches[self.cache_alias].make_key(self.make_key(key))
        client = get_redis_connection()
        return client.srem(key, *values)

    def scard(self, key):
        key = caches[self.cache_alias].make_key(self.make_key(key))
        client = get_redis_connection()
        return client.scard(key)

    def spop(self, key, count=None, decode='utf-8'):
        key = caches[self.cache_alias].make_key(self.make_key(key))
        client = get_redis_connection()
        items = client.spop(key, count=count)
        if not decode:
            return items
        return [item.decode(decode) for item in items]

    def smembers(self, key, decode='utf-8'):
        key = caches[self.cache_alias].make_key(self.make_key(key))
        client = get_redis_connection()
        items = client.smembers(key)
        if not decode:
            return items
        return [item.decode(decode) for item in items]

    def sismember(self, key, value):
        key = caches[self.cache_alias].make_key(self.make_key(key))
        client = get_redis_connection()
        return client.sismember(key, value)


cf_orm_manager = CacheFrameworkOrmManager()
cf_simple_manager = CacheFrameworkSimpleManager()
