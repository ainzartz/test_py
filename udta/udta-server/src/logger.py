# Active recording Session Initiation Protocol daemon (sipd).
# Copyright (C) 2018  Herbert Shin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# https://github.com/initbar/sipd

"""
logger.py
"""

from logging.handlers import TimedRotatingFileHandler

import logging
import os

LOGGING_FORMAT = " ".join(
    [
        u"\u001b[0m[%(asctime)-15s]",
        u"<<\u001b[32;1m%(threadName)s\u001b[0m>>",
        "%(levelname)s",
        u"<\u001b[36m%(filename)s\u001b[0m:\u001b[31;1m%(lineno)s\u001b[0m>",
        "%(message)s",
    ]
)

formatter = logging.Formatter(LOGGING_FORMAT)


def initialize_logger(name, path):
    """ return initialized root logger.
    """
    logger = logging.getLogger()

    # console logging
    logging.basicConfig(level="DEBUG", format=LOGGING_FORMAT)

    # # filesystem logging
    # log_days = 7
    # log_file = name
    # log_path = path
    # if not os.path.exists(log_path):
    #     os.makedirs(log_path)
    # if not log_path.endswith('/'):
    #     log_path += '/'
    # log_path += log_file
    # fs_handler = TimedRotatingFileHandler(
    #     log_path,   # log path
    #     'midnight', # log rotation time
    #     1,          # interval
    #     log_days)   # total logs
    # fs_handler.setFormatter(formatter)
    # fs_handler.suffix = '%Y%m%d'
    # logger.addHandler(fs_handler)

    return logger
