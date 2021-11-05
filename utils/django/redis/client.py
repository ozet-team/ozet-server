# -*- coding: utf-8 -*-
from django_redis.client.default import DefaultClient as BaseClient

from utils.django.redis.lock import Lock


class DefaultClient(BaseClient):
    def lock(self, key, version=None, timeout=None, sleep=0.1,
             blocking_timeout=None, client=None):
        if client is None:
            client = self.get_client(write=True)

        key = self.make_key(key, version=version)
        return client.lock(key,
                           lock_class=Lock,
                           timeout=timeout,
                           sleep=sleep,
                           blocking_timeout=blocking_timeout)
