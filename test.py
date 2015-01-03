# -*- coding: utf-8 -*-

from httplib2 import Http  
from urllib import urlencode
import httplib2
import json


def TestHttpPost():
  word=u'美国'.encode('utf8')
  urlstr = 'http://localhost:8060/recg'
  
  json_data = json.dumps({'imgurl':'http://localhost/imgareaselect/imgs/6.jpg','coordinates':[1301,1007,2448,2048]})
  #print json_data
  data={'key':'sx2767722','info': json_data} 
  
  h = httplib2.Http('.cache')
  response,content = h.request(urlstr, 'POST', urlencode(data), headers={'Content-Type': 'application/x-www-form-urlencoded'})  

  print(response,content)
  
if __name__ == '__main__':  # pragma nocover
  TestHttpPost()
