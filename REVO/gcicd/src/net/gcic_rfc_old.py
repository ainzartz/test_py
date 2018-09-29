#from pyrfc import Connection
import re
import sockets
import json

class GCICIF():
    def __init__(self):
        ASHOST='10.40.77.83'
        CLIENT='100'
        SYSNR='00'
        USER='R_I_IVR_C300'
        PASSWD='gcic2015if'
	self.table = 'ZIF_GET_CALLINFO'
	# max number of rows to return
	self.maxrows = 10
	# starting row to return
	self.fromrow = 0

        #self.FIELDS = ['COMPANY', 'CALL_ID', 'OBJECT_ID', 'CUSTOMER', 'END_CUSTOMER', 'RECIPIENT', 'EMPLOYEE', 'EMPLOYEE_G', 'CIC_PRD', 'CID_SUB_PRD', 'MODEL', 'SERIAL_NO', 'IMEI', 'CATEGORY1', 'CATEGORY2', 'SYMPTOM_CAT1', 'CATEGORY1', 'SYMPTOM_CAT3', 'DETAIL_TYPE', 'ASC_CODE', 'INOUTWTY']

        #self.conn = Connection(ashost=ASHOST, sysnr=SYSNR, client=CLIENT, user=USER, passwd=PASSWD)

    #def qry(self, Fields, SQLTable, Where = '', MaxRows=50, FromRow=0):
    def query(self, company, call_id, MaxRows=50, FromRow=0):
        """A function to query SAP with RFC_READ_TABLE"""

        # By default, if you send a blank value for fields, you get all of them
        # Therefore, we add a select all option, to better mimic SQL.
	Fields = '*'
	SQLTable = self.table
        if Fields[0] == '*':
            Fields = ''
        else:
            Fields = [{'FIELDNAME':x} for x in Fields] # Notice the format

	company_field = 'COMPANY = \'' + company + '\''
	call_id_field = 'CALL_ID = \'' + call_id + '\''
	Where = [company_field, call_id_field]

        # the WHERE part of the query is called "options"
        options = [{'TEXT': x} for x in Where] # again, notice the format

        # we set a maximum number of rows to return, because it's easy to do and
        # greatly speeds up testing queries.
        rowcount = MaxRows

	#print Fields
	#print options

        # Here is the call to SAP's RFC_READ_TABLE
        #tables = self.conn.call("ZIF_GET_CALLINFO", QUERY_TABLE=SQLTable, DELIMITER='|', FIELDS = Fields, \
        #                        OPTIONS=options, ROWCOUNT = MaxRows, ROWSKIPS=FromRow)

        # We split out fields and fields_name to hold the data and the column names
        #fields = []
        #fields_name = []

        data_fields = tables["DATA"] # pull the data part of the result set
        data_names = tables["FIELDS"] # pull the field name part of the result set

	dic_ = {}
	dic_["table"] = "r_ta_result"

	field_size = len(data_fields)
	cols = {}
	for idx in range(0, field_size):
		cols[ data_names[idx]] = data_fields[idx]
	dic_["columns"] = cols
	#print dic_
	js = json.dumps(dic_)
	#print js

	with sockets.safe_allocate_udp_client() as client:
           client.sendto(js, ('127.0.0.1', 8081))
	
	return dic_

	"""
        headers = [x['FIELDNAME'] for x in data_names] # headers extraction
        long_fields = len(data_fields) # data extraction
        long_names = len(data_names) # full headers extraction if you want it

        # now parse the data fields into a list
        for line in range(0, long_fields):
            fields.append(data_fields[line]["WA"].strip())

        # for each line, split the list by the '|' separator
        fields = [x.strip().split('|') for x in fields ]

        # return the 2D list and the headers
        return fields, headers
	"""

"""
# Init the class and connect
# I find this can be very slow to do...
s = GCICIF()

# you need to put a where condition in there... could be anything
where = ['COMPANY = \'C370\'', 'CALL = \'c934\'']

# query SAP
# param: COMPANY, CALL_ID
results, headers = s.qry('C370', '2001fj0454')

print headers
print results
"""
