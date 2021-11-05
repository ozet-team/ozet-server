# -*- coding: utf-8 -*-
try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None

from django.core.cache import cache


class Counter(object):
    KEY_PREFIX = 'counter'

    @classmethod
    def get_cache_key(cls, key):
        return f'{cls.KEY_PREFIX}:{key}'

    @classmethod
    def get_count_by_model(cls, model_cls, pk, attr):
        key = f'{model_cls.__name__}:{attr}:{pk}'
        key = cls.get_cache_key(key)
        return cache.get(key) or 0

    @classmethod
    def get_many_count_by_model(cls, model_cls, pks, attr):
        keys = []
        for pk in pks:
            key = cls.get_cache_key(f'{model_cls.__name__}:{attr}:{pk}')
            keys.append(key)

        rv = cache.get_many(keys)
        items = {k.split(':')[-1]: v for k, v in rv.items()}
        for pk in pks:
            pk_key = str(pk)
            if pk_key in items:
                continue
            items[pk_key] = 0
        return items

    @classmethod
    def get_registered_items_by_model(cls, model_cls, attr):
        items = {}
        prefix = cls.get_cache_key(f'{model_cls.__name__}:{attr}')
        keys = cache.keys(f'{prefix}:*')
        for key in keys:
            try:
                obj_id = int(key.split(':')[-1])
            except ValueError:
                continue
            if obj_id <= 0:
                continue

            cache_client = cache.client
            cache_key = cache_client.make_key(f'{prefix}:{obj_id}', version=None)
            # noinspection PyBroadException
            try:
                redis_client = cache_client.get_client(write=True)
                pipeline = redis_client.pipeline()
                pipeline.get(cache_key)
                pipeline.delete(cache_key)
                rv = pipeline.execute()
            except Exception:
                if sentry_sdk:
                    sentry_sdk.capture_exception()
                continue

            if not rv or rv[0] is None:
                continue

            try:
                v = int(rv[0])
            except ValueError:
                continue

            items[obj_id] = v
        return items

    @classmethod
    def register_by_model(cls, model_cls, pk, attr, count):
        key = f'{model_cls.__name__}:{attr}:{pk}'
        key = cls.get_cache_key(key)
        try:
            count = int(count)
        except ValueError:
            return
        cache.incr(key, count, ignore_key_check=True)
