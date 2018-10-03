from genesys_if import genesys_if
from optimizer import limited_dict

from datetime import datetime, timedelta
import MySQLdb
from contextlib import contextmanager
import gc
import gcic_rfc
import logging
import multiprocessing
import sockets
import time

from threading import Thread

logger = logging.getLogger()


@contextmanager
def create_mysqldb_connection(*a, **kw):
    db = MySQLdb.connect('105.20.2.37', 'minds', 'Minds12#$', 'BIZ', charset='utf8')
    cur = db.cursor()
    try:
        yield (db, cur)
    except Exception as error:
        logger.error("<caught> -> %s", error)
        pass
    finally:
        db.commit()
        cur.close()
        db.close()

def update_genesys_state(conn_id):
    with create_mysqldb_connection() as (db, cur):
        cur.execute("""\
        UPDATE cm_gcicd_deferred_queue
        SET have_genesys = true
        WHERE conn_id = '%s'
        """ % conn_id)


def update_gcic_state(conn_id):
    with create_mysqldb_connection() as (db, cur):
        cur.execute("""\
        UPDATE cm_gcicd_deferred_queue
        SET have_gcic = true
        WHERE conn_id = '%s'
        """ % conn_id)


def remove_defer_entry(conn_id):
    with create_mysqldb_connection() as (db, cur):
        cur.execute("""\
        DELETE FROM cm_gcicd_deferred_queue
        WHERE conn_id = '%s'
        """ % conn_id)


class LazyWorker(object):
    ''' worker implementation.
    '''
    def __init__(self, settings, name='', deferred_worker_size=8):
        self.name = 'worker-' + str(name)
	    self.settings = settings
        # self.deferred_worker_size = max(1, deferred_worker_size)

        # deferred collector thread.
        self.message_queue = multiprocessing.Queue()
	    self.deferred_queue = multiprocessing.Queue()

        # call check logic:
        # ----------------
        # |------|------------------|--> f(t)
        #         \                  \
        #          minimum lifetime   \
        #                             maximum lifetime
	    self.minimum_lifetime = 60 * 3 # seconds
        self.maximum_lifetime = 60 * 60 * 3 # seconds

        # Genesys data cache.
        self.genesys_cache = limited_dict(maxsize=65535)

	self.total_cnt = 0
	self.total_sent_cnt = 0
	self.total_tfn_filtered_cnt = 0
        self.total_expired_cnt = 0
        logger.info('successfully initialized worker: %s', self.name)

    def print_current_state(self):
	    infoString = "Sent: %d,\tQueue: %d,\tExpire: %d,\tFilter: %d" % (
            self.total_sent_cnt,
            self.deferred_queue.qsize(),
            self.total_expired_cnt,
            self.total_tfn_filtered_cnt)
	    logger.info(infoString)

    def initialize(self):
        while True:
            if self.message_queue.empty() and self.deferred_queue.empty():
                time.sleep(1)
                continue

            # collect incoming messages in chunks.
            logger.info("starting new check process: %s left.",
                        self.deferred_queue.qsize())
            chunk = min(500, self.message_queue.qsize())
            while chunk:
                endpoint, payload, recovered = self.message_queue.get()
                logger.info("handling %s from main %s (recovered: %s)",
                            endpoint, payload, recovered)
                try: self.handle(endpoint, payload, recovered)
                finally:
                    chunk -= 1

            # collect deferred messages in chunks.
            logger.info("starting deferred check process: %s left.",
                        self.deferred_queue.qsize())
            chunk = min(1000, self.deferred_queue.qsize())
            while chunk:
                try:
                    work = self.deferred_queue.get()
                    logger.info("handling deferred from main %s", work)
                    if self.handle_deferred(work):
                        self.deferred_queue.put(work)
                finally:
                     chunk -= 1


    #
    # worker interface
    #


    def handle(self, endpoint, payload, recovered):
        ''' worker interface entrypoint.
        @endpoint<tuple> -- server endpoint address.
        @payload<str> -- server socket buffer.
        '''
        logger.info("popped new task: %s", payload)
        if not payload:
            logger.error("no payload received: %s", payload)
            return

        # FIXME: do not eval() user-controlled parameter.
        if isinstance(payload, basestring):
            payload = eval(payload)
	process_type, connid = payload

        # parse message payload.
        logger.info("parsing payload: %s", connid)
        cols = connid.split('|')
        if len(cols) == 2:
            company = cols[0]
            conn_id = cols[1]
        elif len(cols) == 1:
            company = "C310"
            conn_id = cols[0]
        else:
            logger.error("[parsing error] invalid payload format: %s", payload)
            return

        logger.info("parsing parent connid from %s", conn_id)
        if '_' in conn_id:
	    parent_conn_id, transfer_cnt = conn_id.split('_')
	else:
	    parent_conn_id = conn_id
            transfer_cnt = 0

	send_list = []
        self.total_cnt += 1

        # query Genesys.
        logger.info("querying Genesys %s", conn_id)
        with genesys_if() as genesys_connection:
            genesys_ret = genesys_connection.query(parent_conn_id)
            if genesys_ret:
                self.genesys_cache[parent_conn_id] = genesys_ret
                update_genesys_state(conn_id)  # update genesys data.

        # query G-CIC.
        logger.info("querying G-CIC %s", conn_id)
        gcicif = gcic_rfc.GCICIF(self.settings)
        try:
	    gcic_ret = gcicif.query(company, parent_conn_id)
            if gcic_ret:
                update_gcic_state(conn_id)
        finally:
	    gcicif.close()

        # if both G-CIC and Genesys data exists, add to "send list".
        genesys_calltypes = map(lambda x: int(x.get('CALLTYPE')), map(eval, genesys_ret))
        logger.debug("%s calltype is: %s (%s)", conn_id, genesys_calltypes, genesys_ret)
        if (gcic_ret and genesys_ret) or process_type in ['XT', 'AT', 'BT']:
	    send_list.append((process_type, conn_id, genesys_ret, gcic_ret))
            # remove_defer_entry(conn_id)
            logger.info("appended to send_list: %s", conn_id)
        elif genesys_ret and 2 not in genesys_calltypes:
	    send_list.append((process_type, conn_id, genesys_ret, gcic_ret))
            # remove_defer_entry(conn_id)
            logger.info("appended to send_list: %s", conn_id)
	else:
	    now = datetime.now()
	    start = now + timedelta(seconds=self.minimum_lifetime) # time before checking.
	    end = now + timedelta(seconds=self.maximum_lifetime) # time before expiring.
            deferred_data = (process_type, company, conn_id, parent_conn_id, start, end)
            # insert new entry into deferred_queue table.
            with create_mysqldb_connection() as (db, cur):
                query = """\
                INSERT INTO `BIZ`.`cm_gcicd_deferred_queue`\
                (process_type, conn_id, created_dtm, recovered)\
                VALUES ('%s', '%s', now(), %s)""" % (
                    process_type, connid, 'true' if recovered else 'false')
                logger.debug("query-> %s", query)
                cur.execute(query)
	    self.deferred_queue.put(deferred_data)
            logger.info("appended to deferred queue: %s", conn_id)

        # if data exists, send data to endpoint.
        if send_list:
            self._send_sendlist(process_type, send_list)
	self.print_current_state()

        # force garbage collection.
        gc.collect()

    def handle_deferred(self, work):
        '''
        '''
        process_type, company, conn_id, parent_conn_id, start, end = work

        now = datetime.now()
        if now <= start:
            return work

        send_list = []

        # load Genesys data.
        logger.info("deferred checking genesys: %s", conn_id)
        genesys_ret = self.genesys_cache.get(parent_conn_id)
        if not genesys_ret:
            with genesys_if() as connection:
                genesys_ret = connection.query(parent_conn_id)
                if genesys_ret:
                    self.genesys_cache[parent_conn_id] = genesys_ret
                    update_genesys_state(conn_id)
                else:
                    # if there is no Genesys data, there is no need to
                    # go any further since we will always have a mismatch.
                    # Return work to try again next time.
                    if now < end:
                        logger.info("back inside deferred queue: %s", conn_id)
                        return work

        # load G-CIC data.
        logger.info("deferred checking G-CIC: %s", conn_id)
        gcicif = gcic_rfc.GCICIF(self.settings)
        try:
            gcic_ret = gcicif.query(company, parent_conn_id)
            if gcic_ret:
                update_gcic_state(conn_id)
        finally:
            gcicif.close()

        genesys_calltypes = map(lambda x: int(x.get('CALLTYPE')), map(eval, genesys_ret))
        logger.debug("%s calltype is: %s (%s)", conn_id, genesys_calltypes, genesys_ret)
        if now > end or 2 not in genesys_calltypes:
            logger.info("%s had expired or calltype not 2 (calltypes: %s).", conn_id, genesys_calltypes)
            if gcic_ret or genesys_ret:
                send_list.append((process_type, conn_id, genesys_ret, gcic_ret))
                remove_defer_entry(conn_id)
                logger.info("deferred appended to send_list: %s", conn_id)
            else:
                logger.info("deferred no data for %s", conn_id)
            self.genesys_cache.pop(parent_conn_id, None)
            self.total_expired_cnt += 1
            self.total_cnt += 1

        else:
            if gcic_ret and genesys_ret:
                send_list.append((process_type, conn_id, genesys_ret, gcic_ret))
                remove_defer_entry(conn_id)
                logger.info("got Genesys and GCIC data before expiration: %s => GCIC:%s, GENESYS:%s",
                            conn_id, len(gcic_ret), len(genesys_ret))
            # since Genesys and G-CIC data pair is not yet completed, check
            # both sides again before putting back inside the deferred queue.
            else:
                logger.info("back inside deferred queue: %s", conn_id)
                return work

        if send_list:
            self._send_sendlist(process_type, send_list)
        self.print_current_state()

    def _send_sendlist(self, process_type, send_list=[]):
        if not send_list:
            return

        # if there is one transfer call inside the send_list, generate previous
        # transfer call (conn_id) and re-send to the server. Although this
        # will cause extra traffic to be generated, we will always get
        # full transfer transactions immediately instead of waiting for it to
        # be popped from deferred queue.
        # (process_type, conn_id, genesys_ret, gcic_ret)
        for transaction in send_list:
            _, conn_id, _, _ = transaction
            if '_' not in conn_id:
                continue
            parent_conn_id, transfer_cnt = conn_id.split('_')
            transfer_cnt = int(transfer_cnt)
            with sockets.safe_allocate_udp_client() as client:
                # first send parent since it has no transfer tag.
                client.sendto(str(('XT', parent_conn_id)),
                              ('127.0.0.1', 5810))
                logger.info("Re-sending previous transaction: %s", parent_conn_id)

            # send remaining transfers if transfer count is greater than 1.
            if transfer_cnt > 1:
                with sockets.safe_allocate_udp_client() as client:
                    client.sendto(str(('XT', '%s' % parent_conn_id)), ('127.0.0.1', 5810))
                    for i in range(1, transfer_cnt):
                        logger.info("Re-sending previous transaction: %s_%i", parent_conn_id, i)
                        client.sendto(str(('XT', '%s_%s' % (parent_conn_id, i))), ('127.0.0.1', 5810))

        receiver_ip = self.settings["receiver"]["ip"]
        receiver_port = self.settings["receiver"]["port"]
        if len(send_list) != 0:
            if len(send_list) > 10:
                send_listSplit = [ send_list[i:i+10] for i in range(0, len(send_list), 10) ]
                with sockets.safe_allocate_udp_client() as client:
                    for send in send_listSplit:
                        client.sendto(str(send), (receiver_ip, receiver_port))
		    self.statusUpdate(send[1])
	        self.total_sent_cnt += 10
            else:
                with sockets.safe_allocate_udp_client() as client:
                    client.sendto(str(send_list), (receiver_ip, receiver_port))
	        self.statusUpdate(process_type, send_list[0][1])
	        self.total_sent_cnt += len(send_list)
	logger.info("Sending Mysqld %d" % len(send_list))


    def statusUpdate(self, process_type, conn_id):

	update_column = 'meta_collector'
	if process_type in ['BT', 'RE', 'XT', 'AT']:
	    update_column = 'batch'
	elif process_type == 'RT':
	    update_column = 'meta_collector'
	else:
	    update_column = 'meta_collector'

	sql = """
		UPDATE cm_call_status_tb
		SET %s  = now()
		where conn_id = '%s'
	      """ % (update_column, conn_id)

	try:
	    db = MySQLdb.connect('105.20.2.37', 'minds', 'Minds12#$', 'BIZ', charset='utf8')
	    cur = db.cursor()
            cur.execute(sql)
	    db.commit()
	except MySQLdb.Error as e:
            logger.error(e)
            logger.error(sql)
        finally:
            cur.close()
            db.close()
