# pyfiap
# https://github.com/miettal/pyfiap
# 
# Copyright 2012, "miettal" Hiromasa Ihara
# Licensed under the MIT license.

import suds
import uuid
import datetime

import pytz

class FixNamespace(suds.plugin.MessagePlugin):
  def marshalled(self, context):
    context.envelope[1][0][0].setPrefix('ns2')

class APP() :
  def __init__(self, wsdl_url) :
    self.soap_client = suds.client.Client(wsdl_url, plugins=[FixNamespace()])

  def fetch_latest(self, point_id) :
    return self.fetch(point_id, attrName="time", select = "maximum")[0]

  def fetch_latest_1hour(self, point_id) :
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    to = (now - datetime.timedelta(hours=30))
    return self.fetch(point_id, attrName="time", gteq = to)

  def fetch_latest_1day(self, point_id) :
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    to = (now - datetime.timedelta(days=1))
    return self.fetch(point_id, attrName="time", gteq = to)

  def fetch_by_time(self, point_id, from_, to) :
    return self.fetch(point_id, attrName="time", gteq=from_, lteq=to)

  def fetch(self, point_id,
      attrName = None,
      eq = None,
      neq = None,
      lt = None,
      gt = None,
      lteq = None,
      gteq = None,
      select = None) :

    datas = []

    cursor = ""
    while True :
      # build request
      transport_rq = self.soap_client.factory.create('ns0:transport')
      key = self.soap_client.factory.create('ns0:key')

      transport_rq.header.query._id = str(uuid.uuid4())
      transport_rq.header.query._type = "storage"
      transport_rq.header.query._cursor = cursor
      transport_rq.header.query._acceptableSize = 1000
      transport_rq.header.query.key.append(key)
      transport_rq.header.query.key[0]._id = point_id
      transport_rq.header.query.key[0]._attrName = attrName
      transport_rq.header.query.key[0]._eq = eq
      transport_rq.header.query.key[0]._neq = neq
      transport_rq.header.query.key[0]._lt = lt
      transport_rq.header.query.key[0]._gt =  gt
      transport_rq.header.query.key[0]._lteq = lteq
      transport_rq.header.query.key[0]._gteq = gteq
      transport_rq.header.query.key[0]._select = select

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
            datas.append((point_id, value.value, value._time))

      # set next cursor
      if '_cursor' in dir(transport_rs.header.query) :
        cursor = transport_rs.header.query._cursor
      else :
        break

    return datas

  def write(self, point_id, value, time = None) :
    if time == None :
      time = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).isoformat()
    return self.write_([(point_id, value, time)])

  def write_multiple(self, datas) :
    while 0 < len(datas)  :
      self.write_(datas[:5000])
      datas = datas[5000:]

  def write_(self, datas) :
    # build request
    transport_rq = self.soap_client.factory.create('ns0:transport')
    for (point_id, value, time) in datas :
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
      values.append(point_id, value.value, value._time)
  
  return values


if __name__ == "__main__" :
  import pprint
  wsdl_url = "http://..."
  point_id = "http://..."
  app = APP(wsdl_url)

  from_ = (datetime.datetime.now(pytz.utc)-datetime.timedelta(days=3))
  to = datetime.datetime.now(pytz.utc)
  pprint.pprint(app.fetch_by_time(point_id, from_=from_, to=to))
