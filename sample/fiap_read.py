import pyfiap
import datetime

# JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)

fiap = pyfiap.fiap.APP("http://ants.jga.kisarazu.ac.jp/axis2/services/FIAPStorage?wsdl")

result = fiap.fetch_latest('http://j.kisarazu.ac.jp/OpenLaboD/Frame/Weight/TOTAL')
print(result)

result = fiap.fetch_by_time('http://j.kisarazu.ac.jp/OpenLaboD/Frame/Weight/TOTAL', yesterday, today)
print(result)
