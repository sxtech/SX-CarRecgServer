# -*- coding: utf-8 -*-
'''
车辆识别服务，使用python2.7版本，flask框架。
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
#110: No Info Parameter (POST缺少info参数)
'''

import os
import time
import json
import threading
import Queue
import logging
import logging.handlers

from flask import Flask
from flask import request
from flask_restful import reqparse
from flask_restful import abort
from flask_restful import Api
from flask_restful import Resource

import gl
from recg_thread import RecgThread
from iniconf import CarRecgSerIni
from sqlitedb import RSqlite
from requests_func import RequestsFunc


def init_logging(log_file_name):
    """Init for logging"""
    path = os.path.split(log_file_name)
    if os.path.isdir(path[0]):
        pass
    else:
        os.makedirs(path[0])
    logger = logging.getLogger('root')

    rthandler = logging.handlers.RotatingFileHandler(
        log_file_name, maxBytes=100 * 1024 * 1024, backupCount=5)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(filename)s[line:%(lineno)d] \
        [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    rthandler.setFormatter(formatter)
    logger.addHandler(rthandler)


def version():
    return 'SX-CarRecgServer V2.1.0'


app = Flask(__name__)
api = Api(app)


class Hello(Resource):

    def get(self):
        return {'message': "Welcome to use %s" % version()}

class RecgList(Resource):

    def post(self):
        """识别请求信息"""
        if not request.json:
            return {'package': None, 'msg': 'Bad Request', 'code': 101}, 400
        if request.json.get('key', None) not in gl.KEYSDICT:
            return {'package': None, 'msg': 'Key Error', 'code': 105}, 400
        if 'info' not in request.json:
            return {'package': None, 'msg': 'Json Format Error',
                    'code': 106}, 400
        if 'imgurl' not in request.json['info']:
            return {'package': None, 'msg': 'Json Format Error',
                    'code': 106}, 400
        if 'coordinates' not in request.json['info']:
            return {'package': None, 'msg': 'Json Format Error',
                    'code': 106}, 400
        
        user_info = gl.KEYSDICT.get(request.json['key'], None)
        # 回调用的消息队列
        que = Queue.Queue()

        priority = 30
        if gl.P_SIZE[priority] <= user_info['multiple'] * gl.THREADS:
            priority = user_info['priority']
        elif gl.RECGQUE.qsize() > gl.MAXSIZE:
            return {'carinfo': None, 'msg': 'Server Is Busy', 'code': 108,
                    'state': {'threads': gl.THREADS, 'qsize': gl.P_SIZE},
                    'user': user_info}
        else:
            priority += user_info['priority'] + 10

        gl.LOCK.acquire()
        gl.P_SIZE[priority] += 1
        gl.LOCK.release()
        gl.RECGQUE.put((priority, request.json['info'],
                        request.json['key'], que))

        try:
            recginfo = info['queue'].get(timeout=5)
        except Queue.Empty:
            recginfo = {'carinfo': None, 'msg': 'Time Out', 'code': 107}
        finally:
            gl.LOCK.acquire()
            gl.P_SIZE[priority] -= 1
            gl.LOCK.release()

            del que
            
            recginfo['state'] = {'threads': gl.THREADS, 'qsize': gl.P_SIZE}
            
            return recginfo


class StateList(Resource):

    def get(self):
        if not request.json:
            return {'package': None, 'msg': 'Bad Request', 'code': 101}, 400
        if request.json.get('key', None) not in gl.KEYSDICT:
            # 如果KEY不正确返回错误
            return {'package': None, 'msg': 'Key Error', 'code': 105}, 400

        return {'carinfo': None, 'msg': 'State', 'code': 120,
                'state': {'threads': gl.THREADS, 'qsize': gl.P_SIZE},
                'user': gl.KEYSDICT.get(request.json['key'])}


api.add_resource(Hello, '/')
api.add_resource(RecgList, '/recg')
api.add_resource(StateList, '/state')


class RecgServer:
    def __init__(self):
        # 配置文件
        self.crs = CarRecgSerIni()
        self.sysini = self.crs.get_sys_conf()
        self.centreini = self.crs.get_ser_centre_conf()
        # 创建sqlite对象
        self.sl = RSqlite()
        # 创建HTTP函数对象
        self.rf = RequestsFunc()
        # 识别消息优先队列
        gl.RECGQUE = Queue.PriorityQueue()
        # 线程锁
        gl.LOCK = threading.Lock()

        # 创建图片下载文件夹
        self.file = 'img'
        if not os.path.exists(self.file):
            os.makedirs(self.file)
        # 创建图片截取文件夹
        self.file = 'cropimg'
        if not os.path.exists(self.file):
            os.makedirs(self.file)

    def __del__(self):
        gl.IS_QUIT = True
        del self.crs
        del self.sl
        del self.rf

    def join_centre(self, conn=True):
        """连接中心服务器"""
        if conn:
            time.sleep(3)
            threads = self.sysini['threads']
        else:
            threads = -99

        key_list = sorted(gl.KEYSDICT.iteritems(),
                          key=lambda d: d[1]['priority'], reverse=False)

        data = {'ip': self.sysini['selfip'],
                'port': self.sysini['port'],
                'key': key_list[0][0],
                'priority': 10,
                'threads': threads,
                'mark': ''}
        post_data = {'serinfo': json.dumps(data)}
        try:
            urlstr = 'http://%s:%s/%s' % (self.centreini['ip'],
                                          self.sysini['port'], 'join')
            content = self.rf.send_post(urlstr, post_data)
            logger.info(content)
        except Exception as e:
            logger.error(e)

    def main(self):
        for i in self.sl.get_users():
            gl.KEYSDICT[i['key']] = {'priority': i['priority'],
                                     'multiple': i['multiple']}
        # 识别线程数
        gl.THREADS = self.sysini.get('threads', 4)
        # 允许最大数队列为线程数32倍。
        gl.MAXSIZE = gl.THREADS * 32
        # 权限队列数
        gl.P_SIZE = {10: 0, 20: 0, 30: 0}
        # 创建车辆识别线程
        for c in range(gl.THREADS):
            RecgThread(c).start()

        t = threading.Thread(target=self.join_centre)
        t.start()
        # web服务启动
        app.run(host="0.0.0.0", port=self.sysini.get('port', 8060))

if __name__ == '__main__':  # pragma nocover
    init_logging(r'log\carrecgser.log')
    logger = logging.getLogger('root')

    rs = RecgServer()
    rs.main()
