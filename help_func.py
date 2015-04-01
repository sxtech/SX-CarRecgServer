# -*- coding: cp936 -*-
import datetime
import os
import urllib
from urllib import urlencode
import json

import httplib2

class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class UrlError(Exception):
    def __init__(self, value=''):
        self.value = value
    def __str__(self):
        return repr('Url Error')

class HelpFunc:
    def getTime(self):
        return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    def ipToBigint(self,ipaddr):
        ipStrs = ipaddr.split(".")

        return str(int(ipStrs[3]) + int(ipStrs[2])*256 + int(ipStrs[1])*256*256 + int(ipStrs[0])*256*256*256) 


    def bigintToIp(self,intStr):
        bigint = int(intStr)

        first = bigint/(256*256*256)
        rest = bigint - (first*256*256*256)
        
        second = rest/(256*256)
        rest -= second*256*256
        
        third = rest/256    
        fourth = rest - third * 256
        
        return "%d.%d.%d.%d"%(first,second,third,fourth)

    #根据URL地址获取图片到本地
    def get_img_by_url(self,url,path,filename):
        try:
            local = os.path.join(path,filename)
            filename,headers = urllib.urlretrieve(url.replace('\\','/'),local)

            if headers.getheader('Content-Type') != 'image/jpeg':
                raise UrlError(url)
            return filename
        except Exception as e:
            raise UrlError(url)

    def send_post(self,ip,action,port,post_data):
        urlstr = 'http://%s:%s/%s'%(ip,str(port),action)
      
        h = httplib2.Http('.cache')
        response,content = h.request(urlstr, 'POST', urlencode(post_data), headers={'Content-Type': 'application/x-www-form-urlencoded'})  

        return (response,content)

if __name__ == '__main__':
    hf = HelpFunc()
    url = 'http://www.hercity.com/upfiles/2011/09/20110929170027315649.jpg'
    url2 = 'http://www.hercity.com/upfiles/2011/09/20110929170027315642.jpg'
    url3 = 'http://123.jpg'
    url4 = 'http://192.168.1.123/imgareaselect/imgs/1.jpg'
    url5 = 'http://192.168.1.123\\imgareaselect\\imgs\\1.jpg'
    data = {'ip':'192.168.1.321','port':8060,'key':'keys','priority':10,'threads':4,'mark':'test'}

    post_data={'serinfo':json.dumps(data)}
    
    print hf.send_post('127.0.0.1','join',8017,post_data)

    del hf

    
