#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyrfc import Connection
import sockets
import json
from multiprocessing import Queue
import time

class GCICIF():
    def __init__(self, settings):
	self.settings = settings
        MSHOST=settings['db']['gcic']['MSHOST']
        CLIENT=settings['db']['gcic']['CLIENT']
        USER=settings['db']['gcic']['USER']
        PASSWD=settings['db']['gcic']['PASSWD']

        SYSID=settings['db']['gcic']['SYSID']
        SAPROUTER=settings['db']['gcic']['SAPROUTER']
        GROUP=settings['db']['gcic']['GROUP']
        MSSERV=settings['db']['gcic']['MSSERV']
	"""
        ASHOST='105.1.12.58'
	print ASHOST
        CLIENT='100'
        SYSNR='00'
        USER='R_I_IVR_C300'
        PASSWD='gcic2015if'
	"""

        	#self.conn = Connection(ashost=ASHOST, sysnr=SYSNR, client=CLIENT, user=USER, passwd=PASSWD)
        #self.conn = Connection(user=USER, passwd=PASSWD, mshost=MSHOST, msserv=MSSERV, sysid=SYSID, group=GROUP, aprouter=SAPROUTER, client=CLIENT)
	self.conn = Connection(user='R_I_IVR_C300', passwd='gcic2015if', mshost='105.1.12.58', msserv='3600', sysid='CUP', group="IFGRP", saprouter='', client='100')

	#except CommunicationError:
	#	print "RFC_COMMUNICATION_FAILURE"
	#	time.sleep(10)
        #	#self.conn = Connection(ashost=ASHOST, sysnr=SYSNR, client=CLIENT, user=USER, passwd=PASSWD)
        #	self.conn = Connection(user=USER, passwd=PASSWD, mshost=MSHOST, msserv=MSSERV, sysid=SYSID, group=GROUP, aprouter=SAPROUTER, client=CLIENT)
		

    def pp_json(json_thing, sort=True, indents=4):
        return None

    def query(self, company, conn_id):
        """A function to query SAP with RFC_READ_TABLE"""
	it = {}
	it['COMPANY'] = 'C310'
	it['CALL_ID'] = conn_id.upper()

        tables = self.conn.call("ZIF_GET_CALLINFO", IT_LIST = [ it ])
	dic_ = {}
	dic_ = tables
	#print tables
	ret = tables["ET_LIST"]


	#guid = tables["ET_LIST"][0]["GUID"]
	#print tables["ET_LIST"][0]["COUNTRY"]
	#for a in dic_:
	#	print a, dic_[a]
	
	#receiver_ip = self.settings["receiver"]["ip"]
	#receiver_port = self.settings["receiver"]["port"]
	#print receiver_ip, receiver_port
	#with sockets.safe_allocate_udp_client() as client:
        #   client.sendto(str(ret), (receiver_ip, receiver_port))
	return ret
    def close(self):
	self.conn.close()	


if __name__ == '__main__':
    import json
    with open('../../config.json') as f:
        settings = json.loads(f.read())
    a = GCICIF(settings)
    print a.query("C310", "007502c33f25c560")



#    for connid in ['007502c2b9fa55b7','007502c2b9fa6f91','007502c2b9fa6f92','007502c2b9fa6f93','007502c2b9fa6f94','007502c2b9fa6f95','007502c2b9fa6f97','007502c2b9fa7d5a','007502c2b9fa7d5b','007502c2b9fa7d5c','007502c2b9fa7d5f']:
#        print a.query('c310', connid)
