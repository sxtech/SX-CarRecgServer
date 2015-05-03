# -*- coding: utf-8 -*-

from httplib2 import Http  
from urllib import urlencode
import httplib2
import json


def TestHttpPost():
  word=u'美国'.encode('utf8')
  urlstr = 'http://localhost:8060/recg'
  
  json_data = {'imgurl':'http://localhost/imgareaselect/imgs/1.jpg','coordinates':None}
##  url_list = []
##  for i in range(1000):
##    url_list.append('http://localhost/imgareaselect/imgs/1.jpg')
##  json_data = json.dumps(url_list)
  data={'key':'sx2767722_10','info': json_data}
  
  h = httplib2.Http('.cache')
  response,content = h.request(urlstr, 'POST', json.dumps(data), headers={'Content-Type': 'application/json'})  
  print content
  #print json.loads(content)['carinfo'][0]['hphm']
  
if __name__ == '__main__':  # pragma nocover
  TestHttpPost()
