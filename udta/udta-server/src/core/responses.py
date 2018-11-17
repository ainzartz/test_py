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
import json

from lib.lazyproperty import lazyproperty


@attr.s(slots=True)
class Response(object):

    status = None
    status_code = None
    result = attr.ib(default="")  # result computed from client's request

    @lazyproperty
    def json(self):
        return json.dumps(
            {
                "status": self.status,
                "status_code": self.status_code,
                "result": self.result,
            }
        )


@attr.s
class Ok(Response):
    status = "Success"
    status_code = 200


@attr.s
class InvalidRequest(Response):

    status = "Bad Request"
    status_code = 400
    reason = attr.ib(default="")  # failure reason

    @lazyproperty
    def json(self):
        return json.dumps(
            {
                "status": self.status,
                "status_code": self.status_code,
                "reason": self.reason,
            }
        )


@attr.s
class NotFound(InvalidRequest):
    status = "Not Found"
    status_code = 404
    reason = attr.ib(default="")  # failure reason


__all__ = ["InvalidRequest", "Ok", "Response", "NotFound"]
