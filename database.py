
import cx_Oracle

def get_connection():
    dsn_tns = cx_Oracle.makedsn('172.17.100.122', '1521', service_name='UPCHP')
    connection = cx_Oracle.connect(user='USR_IURQUIAGA', password='Y6F3n2%G', dsn=dsn_tns)
    return connection
