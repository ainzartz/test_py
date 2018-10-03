#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import pymssql
import sockets

from multiprocessing import Queue

def genesys_connection():
    server='105.20.2.25'
    user='prism'
    password='CsFJz4/S'
    database='GMAT'
    port='1444'
    return pymssql.connect(host=server,
                           port=port,
                           user=user,
                           password=password,
                           database=database)

template = ' '.join(map(lambda x:x.strip(), '''\
SELECT TENANTID,
       CONNID,
       PARENT_CONNID,
       CALLID,
       PARENTCALLID,
       CALLANI,
       CALLDNIS,
       TENANT_ID,
       CATEGORY,
       LOB,
       SITE_NAME,
       CCGROUP,
       ADD_INFO,
       SKILL_NAME,
       AGENT_ID,
       AGENT_NAME,
       CALLTYPE
FROM GMAT.dbo.VW_REVO_CALL_INFO WITH (NOLOCK)
WHERE CONNID = '%s' order by CREATED_TS ;
'''.split('\n')))

class genesys_if():

    def __init__(self):
	#host = settings['db']['genesys']['host']
	#port = settings['db']['genesys']['port']
	#user = settings['db']['genesys']['user']
	#password = settings['db']['genesys']['password']
	#databse = settings['db']['genesys']['database']
        pass

    def makejson(self, result):
	dic = {}
	dic["TENANTID"] = result[0]
	dic["CONNID"] = result[1]
	dic["PARENT_CONNID"] = result[2]
	dic["CALLID"] = result[3]
	dic["PARENTCALLID"] = result[4]
	dic["CALLANI"] = result[5]
	dic["CALLDNIS"] = result[6]
	dic["TENANT_ID"] = result[7]
	dic["CATEGORY"] = result[8]
	dic["LOB"] = result[9]
	dic["SITE_NAME"] = result[10]
	dic["CCGROUP"] = result[11]
	dic["ADD_INFO"] = result[12]
	dic["SKILL_NAME"] = result[13]
	dic["AGENT_ID"] = result[14]
	dic["AGENT_NAME"] = result[15]
	dic["CALLTYPE"] = result[16]

	#if len(dic["CALLDNIS"]) <= 9:
	#	return "FILTER:" + dic["CALLDNIS"]

	ret = str(dic)
	#print ret
	return ret

    def query(self, connId):
        """A function to query Genesys DB """
        statement = template % connId
	ret = []
        with self.db.cursor() as cursor:
	    cursor.execute(statement)
            result = cursor.fetchall()

	# no vaules
	if result == None:
	    return [] 
	# result fields must hae 16 field values
	#elif len(result) != 17:
	#	jsonStr = str({})
	else:
	    for item in result:
		tempData = self.makejson(item)
		ret.append(tempData)
	    return ret
	#print jsonStr
	#return jsonStr

    def __enter__(self):
        self.db = genesys_connection()
        return self

    def __exit__(self, *a, **kw):
	try:
            self.db.close()
            # print "automatically closed."
        except AttributeError:
            pass # already closed.

    def close(self):
	self.connection.close()

if __name__ == '__main__':
    data = None
    with genesys_if() as connection:
        data = connection.query(connId='007502C33F25C560')
        print len(data), data
    # work with data
