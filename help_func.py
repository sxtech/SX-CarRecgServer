# -*- coding: cp936 -*-
import datetime
import os
import urllib

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
            urllib.urlretrieve(url,local)
            return local
        except Exception,e:
            raise

if __name__ == '__main__':
    hf = HelpFunc()
    url = 'http://www.hercity.com/upfiles/2011/09/20110929170027315649.jpg'
    url2 = 'http://123.jpg'
    print hf.get_img_by_url(url2,'img','test123.jpg')



    
