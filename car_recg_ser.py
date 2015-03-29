# -*- coding: cp936 -*-
'''
车辆识别服务，使用python2.7版本，pulsar框架。
返回代码：
100: Success (识别成功)
101: Request Error (请求错误)
102: Recognise Error (识别错误)
103: Url Error (图片url路径错误)
104: Unknow Error (未知错误)
105: Key Error (用户密钥错误)
106: Json Format Error (json格式错误)
107: Time Out (超时)
108: Server Is Busy (服务繁忙)
109: Recg Server Error (识别服务错误)
110: No Info Parameter (POST缺少info参数)
'''
import urllib
import urlparse
import json
import threading
import Queue
import os
import logging
import logging.handlers

try:
    from pulsar import MethodNotAllowed
except ImportError:  # pragma nocover
    import sys
    sys.path.append('../../')
    from pulsar import MethodNotAllowed

from pulsar.apps import wsgi
from pulsar.apps import socket 

import gl
from recg_thread import RecgThread
from iniconf import CarRecgSerIni
from sqlitedb import U_Sqlite

def initLogging(logFilename):
    """Init for logging"""
    path = os.path.split(logFilename)
    if os.path.isdir(path[0]):
        pass
    else:
        os.makedirs(path[0])
    logger = logging.getLogger('root')
    
    Rthandler = logging.handlers.RotatingFileHandler(logFilename, maxBytes=100*1024*1024,backupCount=5)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    Rthandler.setFormatter(formatter)
    logger.addHandler(Rthandler)

def version():
    return 'SX-CarRecgServer V0.2.1'

def hello(environ, start_response):
    '''The WSGI_ application handler which returns an iterable
    over the "Hello World!" message.'''
    #request_body = environ['wsgi.input']
    if environ['REQUEST_METHOD'] == 'POST' and environ['PATH_INFO']== '/recg':
        data = request_data(environ["wsgi.input"].read())
        status = '200 OK'
    elif environ['REQUEST_METHOD'] == 'POST' and environ['PATH_INFO']== '/state':
        data = state(environ["wsgi.input"].read())
        status = '200 OK'
    else:
        data = json.dumps({'carinfo':None,'msg':'Request Error','code':101})
        status = '400 Request Error'
        
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])

def server(description=None, **kwargs):
    '''Create the :class:`.WSGIServer` running :func:`hello`.'''
    description = description or 'Pulsar Hello World Application'

    return wsgi.WSGIServer(hello, name='RecgServer', description=description, **kwargs)

def state(wsgi_input):
    data = urllib.unquote_plus(wsgi_input)
    post_data = urlparse.parse_qs(data,True)
    
    user_info =  gl.KEYSDICT.get(post_data.get('key',[None])[0],None)
    #如果KEY不正确返回错误
    if user_info is None:
        return json.dumps({'carinfo':None,'msg':'Key Error','code':105})
    else:
        return json.dumps({'carinfo':None,'msg':'State','code':120,'state':{'threads':gl.THREADS,'qsize':gl.P_SIZE},'user':user_info})

def request_data(wsgi_input):
    data = urllib.unquote_plus(wsgi_input)
    post_data = urlparse.parse_qs(data,True)
    #print post_data
    user_info =  gl.KEYSDICT.get(post_data.get('key',[None])[0],None)

    #如果KEY不正确返回错误
    if user_info is None:
        return json.dumps({'carinfo':None,'msg':'Key Error','code':105})
    #JSON格式错误
    if post_data.get('info',None) == None:
        return json.dumps({'carinfo':None,'msg':'No Info Parameter','code':110})
    else:
        try:
            info = json.loads(post_data.get('info',[''])[0])
        except Exception as e:
            logger.error(e)
            return json.dumps({'carinfo':None,'msg':'Json Format Error','code':106})
    info['queue'] = Queue.Queue()

    priority = 30
    if gl.P_SIZE[priority] <= user_info['multiple']*gl.THREADS:
        priority = user_info['priority']
    elif gl.RECGQUE.qsize() > gl.MAXSIZE:
        return json.dumps({'carinfo':None,'msg':'Server Is Busy','code':108,'state':{'threads':gl.THREADS,'qsize':gl.P_SIZE},'user':user_info})
    else:
        priority += user_info['priority'] + 10
        
    gl.LOCK.acquire()
    gl.P_SIZE[priority] += 1
    gl.LOCK.release()
    gl.RECGQUE.put((priority,info,post_data.get('key',[None])[0]))
   
    try:
        recginfo = info['queue'].get(timeout=15)
        recginfo['state'] = {'threads':gl.THREADS,'qsize':gl.P_SIZE}
    except Queue.Empty:
        recginfo = {'carinfo':None,'msg':'Time Out','code':107,'state':{'threads':gl.THREADS,'qsize':gl.P_SIZE}}
    finally:
        gl.LOCK.acquire()
        gl.P_SIZE[priority] -= 1
        gl.LOCK.release()
        return json.dumps(recginfo)
        del info['queue']

class RecgServer:
    def __init__(self):
        self.crs = CarRecgSerIni()
        self.sysini = self.crs.getSysConf()
        self.sl = U_Sqlite()
        gl.RECGQUE = Queue.PriorityQueue()
        gl.LOCK = threading.Lock()

        #创建图片下载文件夹
        self.file = 'img'
        if os.path.exists(self.file) == False:
            os.makedirs(self.file)
        #创建图片截取文件夹
        self.file = 'cropimg'
        if os.path.exists(self.file) == False:
            os.makedirs(self.file)

    def __del__(self):
        del self.crs
        del self.sl
        
    def main(self):
        for i in self.sl.get_users():
            gl.KEYSDICT[i[1]] = {'priority':i[2],'multiple':i[3]}

        gl.THREADS = self.sysini.get('threads',4)
        gl.MAXSIZE = gl.THREADS*32  #允许最大数队列为线程数32倍。
        gl.P_SIZE = {10:0,20:0,30:0} #权限队列数
        #创建车辆识别线程
        for c in range(gl.THREADS):
            RecgThread(c).start()
            
        server().start()

if __name__ == '__main__':  # pragma nocover
    initLogging(r'log\carrecgser.log')
    logger = logging.getLogger('root')
        
    rs = RecgServer()
    rs.main()

