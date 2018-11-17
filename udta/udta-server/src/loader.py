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
loader.py
---------
"""

from __future__ import absolute_import

import sys

from core.server import AsynchronousTCPServer
from lib.lazyproperty import lazyproperty
from ta.worker import ServiceWorker
from version import BRANCH, VERSION


LOGO = """\
/**
 * UDTAS -- %(description)s
 * contact: %(contact)s
 * version: %(branch)s@%(version)s
 */
"""


class Application(object):
    """ application base prototype """

    # application version
    version = "%s-v%s" % (BRANCH, VERSION)

    def __init__(self, settings):
        self.settings = settings
        sys.stderr.write(self.logo)

    @lazyproperty
    def logo(self):
        """ application logo """
        return LOGO % {
            "branch": BRANCH,
            "contact": ["Herbert <herbert@mindslab.ai> Shin"],
            "description": "User-defined TA Server Engine",
            "version": VERSION,
        }

    def run(self, *a, **kw):
        """ run application """
        # `service_worker` processes active and pending tasks in background.
        service_worker = ServiceWorker(daemon=True)
        service_worker.thread.start()

        # `tcp_server` processes all incoming requests from clients.
        tcp_server = AsynchronousTCPServer(self.settings)
        tcp_server.loop.run_forever()


__all__ = ["Application"]
