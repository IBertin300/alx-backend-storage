#!/usr/bin/env python3
"""
Redis module
"""
import sys
from functools import wraps
from typing import Union, Optional, Callable
from uuid import uuid4

import redis

UnionOfTypes = Union[str, bytes, int, float]


def count_calls(method: Callable) -> Callable:
    """
    a system to count how many
    times methods of the Cache class are called.
    :param method:
    :return:
    """
    KEY = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrap
        :param self:
        :param args:
        :param kwargs:
        :return:
        """
        self._redis.incr(KEY)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    add its input parameters to one list
    in redis, and store its output into another list.
    :param method:
    :return:
    """
    KEY = method.__qualname__
    i = "".join([KEY, ":inputs"])
    o = "".join([KEY, ":outputs"])

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapp """
        self._redis.rpush(i, str(args))
        res = method(self, *args, **kwargs)
        self._redis.rpush(o, str(res))
        return res

    return wrapper


class Cache:
    """
    Cache redis class
    """

    def __init__(self):
        """
        constructor of the redis model
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: UnionOfTypes) -> str:
        """
        generate a random key (e.g. using uuid),
         store the input data in Redis using the
          random key and return the key.
        :param data:
        :return:
        """
        KEY = str(uuid4())
        self._redis.mset({KEY: data})
        return KEY

    def get(self, KEY: str, fn: Optional[Callable] = None) \
            -> UnionOfTypes:
        """
        convert the data back
        to the desired format
        :param key:
        :param fn:
        :return:
        """
        if fn:
            return fn(self._redis.get(KEY))
        data = self._redis.get(KEY)
        return data

    def get_int(self: bytes) -> int:
        """get a number"""
        return int.from_bytes(self, sys.byteorder)

    def get_str(self: bytes) -> str:
        """get a string"""
        return self.decode("utf-8")