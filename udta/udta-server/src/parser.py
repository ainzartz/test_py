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
parser.py
---------
"""

from __future__ import absolute_import

import argparse


def parse_arguments():
    """ parse command-line arguments """

    argsparser = argparse.ArgumentParser(
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30)
    )

    argsparser.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="print program version and exit.",
    )

    #
    # server
    #

    server = argsparser.add_argument_group("server arguments")

    server.add_argument(
        "--addr",
        metavar="str",
        type=str,
        default="127.0.0.1",
        help="server listening address (default: '127.0.0.1')",
    )

    server.add_argument(
        "--port",
        metavar="int",
        type=int,
        default="4000",
        help="server listening port (default: 4000)",
    )

    args = argsparser.parse_args()
    return args


__all__ = ["parse_arguments"]
