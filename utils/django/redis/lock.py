# -*- coding: utf-8 -*-
from redis.lock import Lock as BaseLock


class Lock(BaseLock):

    def do_release(self, expected_token):
        self.lua_release(keys=[self.name],
                         args=[expected_token],
                         client=self.redis)
