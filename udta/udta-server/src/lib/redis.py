# MIT License
#
# Copyright (c) 2018 Herbert Shin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
redis.py
--------
"""

from __future__ import absolute_import

import ast
import contextlib
import hashlib
import logging
import redis

try:
    import cPickle as pickle
except ImportError:
    import pickle

from lib.random import validate_identifier

logger = logging.getLogger()


REDIS_PASSWORD = "msl1234~"


@contextlib.contextmanager
def allocate_redis_client(addr: str = "127.0.0.1", port: int = 6379, db: str = 0):
    """ allocate new redis client and safely close it """
    pool = redis.ConnectionPool(host=addr, port=port, password=REDIS_PASSWORD, db=db)
    client = redis.StrictRedis(connection_pool=pool)
    try:
        yield client
    finally:
        pool.disconnect()


def parse_redis_result(result, default=None):
    """ convert redis results into Python objects
    @result<any> -- results from Redis.
    """
    if result is None:
        return default
    elif isinstance(result, bytes):
        # first decode `bytes` into string and safely load as AST object.
        try:
            parsed_result = ast.literal_eval(result.decode())
        except UnicodeDecodeError:
            parsed_result = pickle.loads(result)
    return parsed_result  # otherwise, return Python object.


# common table names
TASK_COUNT = "tasks-count"  # pending tasks count
TASK_QUEUE = "tasks-queue"  # active and pending task queue


def get_task_count(*a, **kw) -> int:
    """ return total tasks count """
    with allocate_redis_client() as client:
        return parse_redis_result(client.get(TASK_COUNT), default=0)


def get_task_queue(*a, **kw) -> list:
    """ return total tasks """
    with allocate_redis_client() as client:
        return parse_redis_result(client.get(TASK_QUEUE), default=[])


def get_key_from_redis(key: str):
    """ get identifier from database
    @key<str> -- redis store key
    """
    if not key:
        return

    with allocate_redis_client() as client:
        return client.get(key)


def add_key_to_redis(key: str, value: dict, noqueue=False, timeout=60 * 60 * 24) -> bool:
    """ add identifier to database
    @key<str> -- redis store key
    @value<dict> -- redis store value
    @timeout<int> -- redis key expiration
    """
    if not key or key in [TASK_COUNT, TASK_QUEUE]:
        return

    with allocate_redis_client() as client:
        queue = get_task_queue()
        if key in queue:
            return

        # update task queue
        queue.append(key)
        if not noqueue:
            client.set(TASK_QUEUE, queue)
            client.incr(TASK_COUNT)  # update pending count
        client.setex(key, timeout, value)

        # update pending count
        logger.debug("successfully added redis key: `%s`", key)
        return get_task_count()
    logger.info("failed to add redis key: `%s`", key)


def delete_key_from_redis(key: str) -> bool:
    """ remove key from database
    @key<str> -- `reference id`
    """
    if key in [TASK_COUNT, TASK_QUEUE]:
        return

    with allocate_redis_client() as client:
        if not client.get(key):
            return

        # delete task and update task queue
        queue = get_task_queue()
        if key in queue:
            queue.pop(queue.index(key))
            client.set(TASK_QUEUE, queue)
            client.decr(TASK_COUNT)  # update pending count
        client.delete(key)

        logger.warning("successfully removed redis key: `%s`", key)
        return get_task_count()
    logger.error("failed to remove redis key: `%s`", key)


__all__ = [
    "TASK_COUNT",
    "TASK_QUEUE",
    "add_key_to_redis",
    "allocate_redis_client",
    "delete_key_from_redis",
    "get_key_from_redis",
    "get_task_count",
    "get_task_queue",
    "parse_redis_result",
]
