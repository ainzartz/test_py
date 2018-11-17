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
__main__.py
-----------
"""

from __future__ import absolute_import

import sys

from loader import Application
from logger import initialize_logger
from parser import parse_arguments


if __name__ == "__main__":

    # parse `-h` and `-v`.
    args = parse_arguments()
    if args.version:
        sys.stderr.write(Application.version)
        sys.exit()

    # initialize the root logger after argument parsing to prevent rogue log
    # file from being created by `-h` and `-v`. Otherwise, parse settings.
    logger = initialize_logger(path="./logs", name="udta.log")

    try:
        app = Application(settings=vars(args))
        app.run()
    except KeyboardInterrupt:
        pass
