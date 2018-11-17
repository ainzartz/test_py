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
impala.py
--------
"""

from __future__ import absolute_import
from impala.dbapi import connect

import contextlib


@contextlib.contextmanager
def allocate_impala_client(
        addr: str = "127.0.0.1",
        port: int = 3306,
        username: str = "root",
        password: str = "",
        db=""):
    """ allocate new Impala client and safely close it
    @addr<str> -- Impala host endpoint
    @port<int> -- Impala host port
    @username<str> -- Impala username
    @password<str> -- Impala password
    @db<str> -- Impala database name
    """
    db = connect(host=addr, port=port)
    cur = db.cursor()
    try:
        yield (db, cur)
    finally:
        cur.close()


__all__ = ["allocate_impala_client"]
