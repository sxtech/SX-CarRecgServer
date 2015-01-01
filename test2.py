'''This example is a simple WSGI_ script which displays
the ``Hello World!`` message. To run the script type::

    python manage.py

To see all options available type::

    python manage.py -h

.. autofunction:: hello

.. autofunction:: server

.. _WSGI: http://www.python.org/dev/peps/pep-3333/
'''
try:
    from pulsar import MethodNotAllowed
except ImportError:  # pragma nocover
    import sys
    sys.path.append('../../')
    from pulsar import MethodNotAllowed

from pulsar.apps import wsgi
import urllib,urlparse
import json
import gl
import threading
import Queue
from recg_thread import RecgThread

def hello(environ, start_response):
    '''The WSGI_ application handler which returns an iterable
    over the "Hello World!" message.'''
    #request_body = environ['wsgi.input']
    
    if environ['REQUEST_METHOD'] == 'POST' and environ['PATH_INFO']== '/recg':
        data = request_data(environ["wsgi.input"].read())
        status = '200 OK'
        response_headers = [
            ('Content-type', 'text/plain'),
            ('Content-Length', str(len(data)))
        ]
        start_response(status, response_headers)
        return iter([data])
    else:
        status = '400 Bad Request'
        response_headers = [
            ('Content-type', 'text/plain'),
            ('Content-Length', str(len('Error')))
        ]
        start_response(status, response_headers)
        return iter(['Error'])


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
        gl.RECGQUE = Queue.Queue()
        for c in range(3):
            RecgThread(c).start()

    def run(self):
        server().start()

if __name__ == '__main__':  # pragma nocover
    rs = RecgServer()

