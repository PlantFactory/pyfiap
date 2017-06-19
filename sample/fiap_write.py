import pyfiap
import datetime

# JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
today = datetime.datetime.now()

fiap = pyfiap.fiap.APP("http://ants.jga.kisarazu.ac.jp/axis2/services/FIAPStorage?wsdl")

fiap.write([['http://test', 123, today]])
