# -*- coding: utf-8 -*-
from django_redis.pool import ConnectionFactory as BaseConnectionFactory
from rediscluster.exceptions import RedisClusterException


class ConnectionFactory(BaseConnectionFactory):

    def get_connection_pool(self, params, retry=0):
        """
        Given a connection parameters, return a new
        connection pool for them.

        Overwrite this method if you want a custom
        behavior on creating connection pool.
        """
        try:
            return super(ConnectionFactory, self).get_connection_pool(params)
        except RedisClusterException as e:
            message = str(e)
            if 'cannot be connected' in message and retry < 3:
                return self.get_connection_pool(params, retry=retry + 1)
            raise e
