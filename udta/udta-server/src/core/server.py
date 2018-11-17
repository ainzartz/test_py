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
server.py
---------
"""

from __future__ import absolute_import

import asyncio
import logging
import sys

from core.worker import Worker

if sys.version_info >= (3, 5):
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger()


class AsynchronousTCPServer(object):
    """ Asynchronous TCP server """

    def __init__(self, settings):
        self.settings = settings
        host, port = settings.get("addr", "127.0.0.1"), settings.get("port", 4000)
        self.loop = asyncio.get_event_loop()
        self.instance = self.loop.run_until_complete(
            self.loop.create_server(
                protocol_factory=Worker,
                host=host,
                port=port,
                backlog=128,
                # reuse_address=True,
                # reuse_port=True,
            )
        )
        logger.debug("initialized %s", self)

    def __repr__(self):
        return "%s(settings=%s)" % (self.__class__.__name__, self.settings)


__all__ = ["AsynchronousTCPServer"]
