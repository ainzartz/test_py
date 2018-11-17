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
from collections import namedtuple
from multiprocessing import Process

import attr
import contextlib
import json
import logging
import os
import socket
import time

from lib.impala import allocate_impala_client
from lib.mysql import allocate_mysql_client
from lib.sockets import allocate_tcp_client
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

try:
    import cPickle as pickle
except ImportError:
    import pickle

logger = logging.getLogger()


#
# service worker
#


def background_service(*a, **kw):
    # `SERVICE_LOOP_INTERVAL` determines how frequently the `ServiceWorker`
    # should wake up and check if there is anything to process. If there is
    # no work, then `ServiceWorker` should sleep the maximum of configured
    # time. Otherwise, sleep the minimum of configured time.
    SERVICE_LOOP_INTERVAL = {"fast": 0.05, "slow": 1}  # seconds
    while True:
        try:
            if not get_task_count():
                time.sleep(SERVICE_LOOP_INTERVAL["slow"])
                continue

            # retrieve staged data ("staging") to restore previous session.
            # If there is no data available in "staging", that means we should
            # pick a data from task queue and stage by populating the staging.
            stage = parse_redis_result(get_key_from_redis("staging"))
            if stage is not None:
                task_name = stage["task_name"]
                logger.info("recovered `%s`: %s", task_name, stage)
            else:
                try:
                    # retrieve the oldest task in queue while preserving the
                    # original queue inside the Redis. By doing so, if this
                    # process unexpectedly restarts, we can still pick up from
                    # where we have left off.
                    task_name = get_task_queue().pop(0)  # oldest task
                except IndexError:
                    time.sleep(SERVICE_LOOP_INTERVAL["slow"])
                    continue

                # if "staging" is still empty after trying to populate it with
                # the oldest task, then the task probably is invalid.
                stage = prepare_staging(task_name=task_name)

            if stage is None:
                logger.warning("failed to stage with task: `%s`", task_name)
                delete_key_from_redis(key="staging")
                delete_key_from_redis(key=task_name)
                continue

            # load TA Hmd and Dnn
            task = parse_redis_result(get_key_from_redis(task_name))
            servers = namedtuple(
                "Server",
                " ".join(
                    [
                        "addr",
                        "dnn_engines",
                        "dnn_models",
                        "hmd_engines",
                        "hmd_models",
                        "port",
                    ]
                ),
            )
            ta_servers = servers(
                addr=task["udta_engine"]["addr"],
                dnn_models=task["task"]["dnn_models"],
                dnn_engines=task["ta_engine"]["dnn"],
                hmd_models=task["task"]["hmd_models"],
                hmd_engines=task["ta_engine"]["hmd"],
                port=task["udta_engine"]["port"],
            )

            # analze TA hmd/dnn of staging tasks. All results will be pushed
            # inside the Redis database in order to minimize Process weight.
            analyze_text(ta_servers, queue=stage.get("key_codes", []))

            # TODO: insert into database
            logger.info("[TODO] inserting ta results into MSSQL database.")

            # upon task completion, garbage collect task and remaining data.
            logger.info("task finished: garbage collecting `%s`.", task_name)
            delete_key_from_redis(key=task_name)
            delete_key_from_redis(key="staging")
            for task_name in stage.get("key_codes", []):
                delete_key_from_redis(key=task_name)
        except KeyboardInterrupt:
            pass


@attr.s(frozen=True, slots=True)
class ServiceWorker(object):
    """ service worker """
    daemon = attr.ib(default=True)
    thread = attr.ib(default=Process(target=background_service, daemon=daemon))


#
# staging
#


RESERVED_KEYS = {"KEY_CODE", "KEY_ID", "KEY_SENTENCE"}



def prepare_staging(task_name: str) -> dict:
    """
    @task_name<str> -- task task_name string ("task_name").
    """
    # if this particular task was killed, then the task description will not
    # exist in Redis. Discard this iteration and move on to the next task.
    task = parse_redis_result(get_key_from_redis(task_name))
    if task is None:
        return

    # read given SQL template files and execute to retrieve results. The query
    # must be complete (no error) - but should also account for failures.
    sql_file = task["task"]["sql_filepath"]
    try:
        with open(sql_file) as f:
            sql_query = f.read().strip()
    except FileNotFoundError as error:
        logger.error(error)
        return

    stage = {"task_name": task_name, "task": task, "key_codes": []}

    if task["task"]["sql_type"]["mysql"]:
        key_codes = populate_stage_with_mysql(task["auth"]["mysql"], sql_query)
        stage["key_codes"] = key_codes
    elif task["task"]["sql_type"]["impala"]:
        key_codes = populate_stage_with_impala(task["auth"]["impala"], sql_query)
        stage["key_codes"] = key_codes

    # update staging in Redis
    add_key_to_redis("staging", stage, noqueue=True)
    return stage


def populate_stage_with_mysql(mysql_conf: dict, sql_query: str):
    """
    """
    with allocate_mysql_client(
            addr=mysql_conf["addr"],
            port=mysql_conf["port"],
            username=mysql_conf["user"],
            password=mysql_conf["pass"],
            db=mysql_conf["db_name"]
    ) as (db, cur):
        try:
            cur.execute(sql_query)  # Note: extremely insecure..
            if cur.rowcount is 0:
                logger.warning("no rows returned from execution.")
                return []
        except Exception as error:
            logger.error(error)
            return []

        # extract column names to dynamically parse query results. For any
        # error checks, make sure reserved words are used in columns.
        columns = [str(column[0]).upper() for column in cur.description]
        if len(RESERVED_KEYS) != len(RESERVED_KEYS & set(columns)):
            logger.critical("%s missing in sql results: %s" % RESERVED_KEYS)
            return []

        key_codes = []

        # parse and convert each rows into easily manipulative objects. Each
        # keys will be its own expirable entry in Redis -- all referenced
        # by the staging's `task` key.
        Row = namedtuple("Row", " ".join(columns))
        for _ in range(cur.rowcount):
            row = cur.fetchone()

            # convert each rows into namedtuple representation and store
            # the pickled representations into the redis database.
            _row = Row(**dict(zip(columns, row)))
            _row_pickle = pickle.dumps(_row._asdict())
            add_key_to_redis(_row.KEY_CODE, _row_pickle, noqueue=True)
            key_codes.append(_row.KEY_CODE)

        return key_codes


def populate_stage_with_impala(impala_conf: dict, sql_query: str):
    """
    """
    with allocate_impala_client(
            host=impala_conf["addr"],
            port=impala_conf["port"],
            user=impala_conf["user"],
            password=impala_conf["pass"],
            database=impala_conf["db_name"]
    ) as (db, cur):
        try:
            cur.execute(sql_query)  # Note: extremely insecure..
            if cur.rowcount is 0:
                logger.warning("no rows returned from execution.")
                return []
        except Exception as error:
            logger.error(error)
            return []

        # extract column names to dynamically parse query results. For any
        # error checks, make sure reserved words are used in columns.
        columns = [str(column[0]).upper() for column in cur.description]
        if len(RESERVED_KEYS) != len(RESERVED_KEYS & set(columns)):
            logger.critical("%s missing in sql results: %s" % RESERVED_KEYS)
            return []

        key_codes = []

        # parse and convert each rows into easily manipulative objects. Each
        # keys will be its own expirable entry in Redis -- all referenced
        # by the staging's `task` key.
        Row = namedtuple("Row", " ".join(columns))
        for _ in range(cur.rowcount):
            row = cur.fetchone()

            # convert each rows into namedtuple representation and store
            # the pickled representations into the redis database.
            _row = Row(**dict(zip(columns, row)))
            _row_pickle = pickle.dumps(_row._asdict())
            add_key_to_redis(_row.KEY_CODE, _row_pickle, noqueue=True)
            key_codes.append(_row.KEY_CODE)

        return key_codes


#
# Text-analysis client
#


def analyze_text(ta_servers: dict, queue: list = []):
    """
    """
    if not queue:
        return

    for task_name in queue:
        task = parse_redis_result(get_key_from_redis(key=task_name))
        sentence = task["KEY_SENTENCE"]
        spec = {
            "text": sentence,
            "hmd": {
                "model_name": ta_servers.hmd_models,
                "engines": ta_servers.hmd_engines,
            },
            "dnn": {
                "model_name": ta_servers.dnn_models,
                "engines": ta_servers.dnn_engines,
            },
        }
        logger.info("analyzing ta structure => %s", spec)

        with allocate_tcp_client() as tcp_client:
            tcp_client.connect((ta_servers.addr, ta_servers.port))
            tcp_client.send(json.dumps(spec).encode())
            buf = tcp_client.recv(1024)
            result = json.loads(buf.decode())
            logger.debug("received ta structure => %s", result)

        # TODO: write results to file or insert into database.
