# -*- coding: utf-8 -*-
import json

import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

def get_url_img(url, path):
    """根据URL地址抓图到本地文件"""
    try:
        r = requests.get(url, stream=True)

        if r.status_code == 200:
            with open(path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        # 非200响应,抛出异常
        r.raise_for_status()
    except:
        raise
    
def requests_test():
    url = 'http://127.0.0.1:8060/v1/recg'
    json_data = {'imgurl' : 'http://localhost/imgareaselect/imgs/1.jpg',
                 'coord': []}
    r = requests.post(url, data=json.dumps(json_data),
                      headers={'content-type' : 'application/json'},
                      auth=HTTPBasicAuth('kakou', 'carrecgkakou'))
    print r.text
    print r.status_code

# 上传文件识别测试
def uploadrecg_test():
    url = 'http://127.0.0.1:8060/v1/uploadrecg'
    json_data = {'coord': []}
    files = {'file': open('000.jpg', 'rb')}
    r = requests.post(url, files=files,
                      auth=HTTPBasicAuth('kakou', 'carrecgkakou'))
    print r.text
    print r.status_code

if __name__ == '__main__':
    #requests_test()
    uploadrecg_test()
##    url = 'http://localhost/imgareaselect/imgs/1123.jpg'
##    path = 'img/test.jpg'
##    try:
##        get_url_img(url, path)
##    except Exception as e:
##        print e

