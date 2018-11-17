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

import attr
import datetime
import json
import logging

logger = logging.getLogger()


#
# Request objects
# ---------------
# Note: all client request should be converted into a `Request` object.
#


@attr.s(slots=True)
class Request(object):
    """ base client request object
    @command<str> -- remote procedure call to invoke a respective handler.
    @body<dict> -- request payload.
    """

    # `command` must invoke a handler defined in the `server.py`. Otherwise,
    # it will revert to default handler (drop request).
    command = attr.ib(default=None)
    payload = attr.ib(default={})

    # auto-generated metadata below:
    timestamp = attr.ib(default=None)  # time the request was first arrived.

    def __repr__(self):
        return "%s(command=%s, payload=%s, timestamp=%s)" % (
            self.__class__.__name__,
            self.command,
            self.payload,
            self.timestamp,
        )


@attr.s(frozen=True)
class GoodRequest(Request):
    pass  # client's request is accepted.


@attr.s(frozen=True)
class DropInvalidFormat(Request):
    pass  # client's request is invalid.


#
# Request parser
# --------------
#


def parse_request(text: str = "{}"):
    """ parse json requests to a `Request` object
    @text<str> -- json string in plaintext.
    """

    if not isinstance(text, (str,)) or len(text) <= 2:
        logger.debug("parsed empty request => %s", text)
        return DropInvalidFormat()  # `handler_default`

    try:
        payload = json.loads(text)
        request = GoodRequest(
            command=payload.get("Command"),
            payload=json.loads(payload.get("Payload")),
            timestamp=datetime.datetime.now(),
        )
        logger.debug("parsed valid request => %s", request)
        return request
    except ValueError:
        logger.error("parsed invalid request => %s", " ".join(text.split()))
        return DropInvalidFormat(command="reject-invalid-format")


__all__ = ["DropInvalidFormat", "GoodRequest", "Request", "parse_request"]
