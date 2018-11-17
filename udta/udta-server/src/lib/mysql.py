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
mysql.py
--------
"""

from __future__ import absolute_import

import MySQLdb as mysqldb
import contextlib


@contextlib.contextmanager
def allocate_mysql_client(
        addr: str = "127.0.0.1",
        port: int = 3306,
        username: str = "root",
        password: str = "",
        db="") -> (mysqldb, mysqldb):
    """ allocate new MySQL client and safely close it
    @addr<str> -- MySQL host endpoint
    @port<int> -- MySQL host port
    @username<str> -- MySQL username
    @password<str> -- MySQL password
    @db<str> -- MySQL database name
    """
    db = mysqldb.connect(host=addr, port=port, user=username, passwd=password, db=db)
    try:
        cur = db.cursor()
        yield (db, cur)
    finally:
        if cur:
            cur.close()


__all__ = ["allocate_mysql_client"]
