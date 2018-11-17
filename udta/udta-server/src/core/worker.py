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

from __future__ import absolute_import

import asyncio
import logging

from core.requests import Request, parse_request
from core.responses import InvalidRequest, Ok, NotFound
from lib.random import generate_random_identifier, validate_identifier
from lib.redis import (
    TASK_COUNT,
    TASK_QUEUE,
    add_key_to_redis,
    allocate_redis_client,
    delete_key_from_redis,
    get_key_from_redis,
    get_task_count,
    get_task_queue,
    parse_redis_result,
)

logger = logging.getLogger()


#
# handlers: default
#


def handler_default(*a, **kw) -> InvalidRequest:
    """ default request handler """
    return InvalidRequest(reason="no handler available for requested `command`")


def handler_drop_invalid_format(*a, **kw) -> InvalidRequest:
    """ one or more request parameters are invalid """
    return InvalidRequest(reason="client has sent invalid json structure")


#
# handlers: job
#


def handler_index_tasks(*a, **kw) -> Ok:
    """ get currently running and queued jobs """
    count, queue = get_task_count(), get_task_queue()
    return Ok(result={"pending-count": count, "pending-tasks": queue})


def handler_add_task(req: Request) -> Ok:
    """ add a new job to work queue
    @req<Request> -- parsed client request object.
    """
    # extract custom name for this session or create a random one.
    task_name = req.payload["task"]["name"] or generate_random_identifier()
    count = add_key_to_redis(key=task_name, value=req.payload)
    if count is None:
        return InvalidRequest(reason="task `%s` already exists" % task_name)
    return Ok(result={"pending-count": count, "task-name": task_name})


def handler_kill_task(req: Request) -> Ok:
    """ kill currently running or queued jobs """
    task_name = req.payload["task"]["name"]
    count = delete_key_from_redis(key=task_name)
    if count is None:
        return NotFound(reason="provided task not found in pending tasks")
    return Ok(result={"pending-count": count})


#
# worker
#


# Note: `Worker` will use `command` parameter to process which handler to use
# for incoming data. By default, `handler_default` is used to drop requests.
# Create a new handler as a function above and add the reference key below.
handlers = {
    "Default": handler_default,
    "get-task-status": handler_index_tasks,
    "kill-task": handler_kill_task,
    "register-new-task": handler_add_task,
    "reject-invalid-format": handler_drop_invalid_format,
}


class Worker(asyncio.Protocol):
    """ asynchronous worker """

    def connection_made(self, transport: tuple):
        """ connection stage """
        self.transport = transport
        # self.endpoint = transport.get_extra_info("peername")

    def data_received(self, data: bytearray):
        """ processing stage """
        try:
            # since incoming requests are `bytearray` type, decode them
            # into a string in order to properly evaluate them into dict.
            # `parse_request` must return a `Request`.
            req = parse_request(data.decode().strip())

            # handler implementations must return a `Response`.
            res = handlers.get(req.command, handlers["Default"])(req=req)
            self.transport.write(res.json.encode())
            logger.info("sent reply to client => %s", res)
        finally:
            self.transport.close()


__all__ = ["Worker"]
