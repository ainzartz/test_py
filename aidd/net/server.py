import MySQLdb
import asyncore
import errno
import hashlib
import logging
import multiprocessing
import random
import sys
import time

from contextlib import contextmanager
from collections import deque
from multiprocessing import Process
from multiprocessing import cpu_count
from net.sockets import safe_allocate_udp_server
#from net.worker import LazyWorker
from threading import Thread

logger = logging.getLogger()

#
#

@contextmanager
def create_mysqldb_connection(*a, **kw):
    db = MySQLdb.connect('105.20.2.37', 'minds', 'Minds12#$', 'BIZ', charset='utf8')
    cur = db.cursor()
    try:
        yield (db, cur)
    finally:
        db.commit()
        cur.close()
        db.close()

# message hashling
#-------------------------------------------------------------------------------

def convert_string_to_number(message):
    digest = hashlib.sha256(message).hexdigest()
    number = int(digest, 16) # type: long
    return number

# server
#-------------------------------------------------------------------------------

class AsynchronousServer(object):
    ''' Asynchronous SIP server to initialize router and globalize settings.
    '''
    def __init__(self, setting):
        if not setting:
            sys.exit(errno.EINVAL)
        self.settings = setting
        print(self.settings)
        logger.info('successfully initialized server.')

    def serve(self):
        try:
            port = int(self.settings['router']['port'])
            logger.info('Listening Port # %s', port)
        except KeyError:
            port = 8080 # udp
        # assign asynchronous handler to the receiving port. Currently,
        # `asyncore` module was chosen in order to provide backward
        # compatibility with Python 2 (where there's no `asyncio`). All
        # incoming traffic is routed and initially handled by the router.
        # with safe_allocate_udp_server(port=port) as socket:
        #     self.router = AsynchronousRouter(self.settings, socket)
        #     self.router.initialize_consumer()
        #     asyncore.loop() # push new events to the event loop.

class AsynchronousRouter(asyncore.dispatcher):
    ''' Asynchronous SIP router to demultiplex and delegate work to workers.
    '''
    def __init__(self, settings, socket):
        # in order to prevent double creation of a router socket, inherit
        # SIP port from SIP server. A router should only be used to receive
        # traffic from the remote endpoint.
        asyncore.dispatcher.__init__(self, socket)
        self.settings = settings

        # override to read-only.
        self.is_readable = True
        self.readable = lambda: self.is_readable
        # self.handle_read = lambda: None

        # override to disable write.
        self.is_writable = False
        self.writable = lambda: self.is_writable
        self.handle_write = lambda: None

        # handled count.
        self.total_handled_cnt = 0

        try: # calculate worker pool size.
            self._pool_size = self.settings['worker']['count']
            if self._pool_size <= 0:
                self._pool_size = cpu_count()
        except KeyError:
            self._pool_size = 1

    def handle_read(self):
        try: # router only receives data ("work") and delegate to worker(s).
            packet = self.recvfrom(0xffff) # max receive bytes.
            endpoint, payload = tuple(packet[1]), str(packet[0])
            self._demux.put((endpoint, payload, False)) # demultiplex.
        except EOFError:
            pass

    def initialize_consumer(self):
        ''' initialize consumer thread.
        '''
        self._demux = multiprocessing.Queue()  # demultiplexer
        # pre-generate workers and worker-threads in order to correctly
        # distribute incoming work without random guessing.
        worker_pool = [
            LazyWorker(self.settings, worker_name)
            for worker_name in range(self._pool_size)
        ]
        worker_threads = []
        for worker in worker_pool:
            thread = Thread(
                name=worker.name,
                target=worker.initialize)
            worker_threads.append(thread)
            thread.daemon = True
            thread.start()

        def consume():
            """
            """
            # recover old session entries.
            logger.info("recovering old session..")
            with create_mysqldb_connection() as (db, cur):
                cur.execute("""\
                SELECT process_type, conn_id
                FROM cm_gcicd_deferred_queue""")
                results = cur.fetchall()
                for result in results:
                    self._demux.put(("", str(result), True))
                logger.info("recovered %s entries -> %s", len(results))

            # delete older entries.
            with create_mysqldb_connection() as (db, cur):
                cur.execute("""DELETE FROM cm_gcicd_deferred_queue WHERE 1=1""")
                logger.info("flushed old entries.")

            while True:
                # if queue is overflowing with processes, then wait until we
                # escape the pool size limitation set by the configuration.
                if self._demux.empty():
                    time.sleep(0.1)
                    continue

                while not self._demux.empty():
                    # ensure no workers are generated more than available work.
                    # otherwise, dispatch messages to a designated worker. In order
                    # to consistently distribute to workers, convert Conn-ID into
                    # integer variation of hashed Conn-ID string.
                    endpoint, payload, recovered = self._demux.get()
                    logger.info('received %s from %s (recovered? %s)',
                                endpoint, payload, recovered)

                    # hash-distribute incoming payloads to endpoint.
                    # index = int(convert_string_to_number(payload) % self._pool_size)
                    # worker_pool[index].message_queue.put((endpoint, (processType, connid)))

                    worker = random.choice(worker_pool)
                    logger.info("pushing into queue: %s", payload)
                    worker.message_queue.put((endpoint, eval(payload), recovered))
                    logger.info("pushed into queue: %s", payload)

                    # print total handled Conn-ID counts.
                    self.total_handled_cnt += 1
                    logger.debug('server statistics: handled: %s (backlog: %s)',
                                 self.total_handled_cnt, self._demux.qsize())
                    # for worker in worker_pool:
                    #     logger.debug('%s statistics: handled: %s (backlog: %s)',
                    #                  worker.name,
                    #                  worker.message_queue.qsize(),
                    #                  worker.deferred_queue.qsize())
        self.__consumer = Thread(name='server', target=consume)
        self.__consumer.daemon = True
        self.__consumer.start()
