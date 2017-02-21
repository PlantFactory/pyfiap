# pyfiap
# https://github.com/miettal/pyfiap
# 
# Copyright 2016, Hiromasa Ihara
# Licensed under the MIT license.

# note:suds-jurko
from suds.client import Client
import uuid
from datetime import *

# for gzip transport
from suds.transport.http import HttpTransport
import gzip
from StringIO import StringIO

class GzipTransport(HttpTransport) :
  def send(self, request):
    request.headers['Accept-encoding'] = 'gzip'
    result = HttpTransport.send(self, request)
    if ('content-encoding' in result.headers and
        result.headers['content-encoding'] == 'gzip') :
      buf = StringIO(result.message)
      f = gzip.GzipFile(fileobj=buf)
      result.message = f.read()
    return result

class APP() :
  def __init__(self, wsdl_url) :
    self.soap_client = Client(wsdl_url, transport=GzipTransport())

  def fetch_latest(self, point_ids) :
    if type(point_ids) != list :
      point_ids = [point_ids]

    keys = []
    for point_id in point_ids :
      keys.append({
        'point_id': point_id,
        'attrName': "time",
        'select': "maximum",
      })

    return self.fetch(keys)

  def fetch_by_time(self, point_ids, from_, to) :
    if type(point_ids) != list :
      point_ids = [point_ids]

    keys = []
    for point_id in point_ids :
      keys.append({
        'point_id': point_id,
        'attrName': "time",
        'gteq': from_,
        'lteq': to,
      })

    return self.fetch(keys)

  def fetch(self, keys) :
    if type(keys) != list :
      keys = [keys]

    data = []

    cursor = ""
    while True :
      # build request
      transport_rq = self.soap_client.factory.create('ns0:transport')

      transport_rq.header.query._id = str(uuid.uuid4())
      transport_rq.header.query._type = "storage"
      transport_rq.header.query._cursor = cursor
      transport_rq.header.query._acceptableSize = 1000

      for key_ in keys :
        key = self.soap_client.factory.create('ns0:key')
        key._id = key_["point_id"]
        key._attrName = key_["attrName"]
        if "eq" in key_ : key._eq = key_["eq"]
        if "neq" in key_ : key._neq = key_["neq"]
        if "lt" in key_ : key._lt = key_["lt"]
        if "gt" in key_ : key._gt =  key_["gt"]
        if "lteq" in key_ : key._lteq = key_["lteq"]
        if "gteq" in key_ : key._gteq = key_["gteq"]
        if "select" in key_ : key._select = key_["select"]
        transport_rq.header.query.key.append(key)

      # dummy
      transport_rq.header.error._type = "DUMMY"

      # fetch
      transport_rs = self.soap_client.service.query(transport_rq)
      if 'OK' in dir(transport_rs.header) :
        pass
      else :
        raise Exception(transport_rs.header.error.value)

      # add point_data
      if 'point_set' in dir(transport_rs.body) :
        for point_set_child in transport_rs.body.point_set:
          data += concat_point_set(point_set_child)

      for point in transport_rs.body.point:
        point_id = point._id
        if 'value' in dir(point) :
          for value in point.value :
            data.append({
              "point_id":point_id,
              "value":value.value,
              "time":value._time})

      # set next cursor
      if '_cursor' in dir(transport_rs.header.query) :
        cursor = transport_rs.header.query._cursor
      else :
        break

    return data

  def write(self, data) :
    if type(data) != list :
      data = [data]
    # build request
    transport_rq = self.soap_client.factory.create('ns0:transport')
    for (point_id, value, time) in data :
      point = self.soap_client.factory.create('ns0:point')
      value_ = self.soap_client.factory.create('ns0:value')
      value_.value = value
      value_._time = time
      point._id = point_id
      point.value = value_
      transport_rq.body.point.append(point)

    # fetch
    transport_rs = self.soap_client.service.data(transport_rq)

    if 'OK' in dir(transport_rs.header) :
      pass
    else :
      raise Exception(transport_rs.header.error.value)

def concat_point_set(point_set) :
  values = []
  if 'point_set' in point_set :
    for point_set_child in point_set.point_set:
      values += concat_point_set(point_set_child)

  for point_child in point_set.point :
    point_id = point_child._id
    for value in point.value :
      values.append({"point_id":point_id,
        "value":value.value,
        "time":value._time})
  
  return values


if __name__ == "__main__" :
  import pprint
  wsdl_url = "http://fiap-dev.gutp.ic.i.u-tokyo.ac.jp/axis2/services/FIAPStorage?wsdl"
  point_id = "http://..."
  app = APP(wsdl_url)

  from_ = (datetime.now()-timedelta(days=3))
  to = datetime.now()
  pprint.pprint(app.fetch_by_time(point_id, from_=from_, to=to))
