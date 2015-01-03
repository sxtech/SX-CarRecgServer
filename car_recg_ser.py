# -*- coding: cp936 -*-
'''This example is a simple WSGI_ script which displays
the ``Hello World!`` message. To run the script type::

    python manage.py

To see all options available type::

    python manage.py -h

.. autofunction:: hello

.. autofunction:: server

.. _WSGI: http://www.python.org/dev/peps/pep-3333/
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

import gl
from recg_thread import RecgThread
from iniconf import CarRecgSerIni

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
    return 'SX-CarRecgServer V0.1.0'

def hello(environ, start_response):
    '''The WSGI_ application handler which returns an iterable
    over the "Hello World!" message.'''
    #request_body = environ['wsgi.input']
    print environ
    if environ['REQUEST_METHOD'] == 'POST' and environ['PATH_INFO']== '/recg':
        data = request_data(environ["wsgi.input"].read())
        status = '200 OK'
    else:
        data = json.dumps({'carinfo':None,'msg':'Request Error','code':101})
        status = '400 Bad Request'
        
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

def request_data(wsgi_input):
    data = urllib.unquote_plus(wsgi_input)
    post_data = urlparse.parse_qs(data,True)
    if post_data.get('key',None)[0] != 'sx2767722':
        return json.dumps({'carinfo':None,'msg':'Key Error','code':105})
    
    if post_data.get('info',None) == None:
        return json.dumps({'carinfo':None,'msg':'Json Format Error','code':106})

    info = json.loads(post_data.get('info',[''])[0])

    info['queue'] = Queue.Queue()
    gl.RECGQUE.put(info)
    try:
        recginfo = info['queue'].get(timeout=15)
        return json.dumps(recginfo)
    except Queue.Empty:
        return json.dumps({'carinfo':None,'msg':'Time Out','code':107})

class RecgServer:
    def __init__(self):
        self.crs = CarRecgSerIni()
        self.sys_ini = self.crs.getSysConf()
        gl.RECGQUE = Queue.Queue()
        #创建车辆识别线程
        for c in range(self.sys_ini.get('threads',4)):
            RecgThread(c).start()

    def main(self):
        server().start()

if __name__ == '__main__':  # pragma nocover
    initLogging(r'log\carrecgser.log')
    logger = logging.getLogger('root')
        
    rs = RecgServer()
    rs.main()

