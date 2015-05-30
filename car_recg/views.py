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

from flask import g, request
from flask_restful import reqparse, abort, Resource

from app import app, db, api
from models import User
import gl
from requests_func import RequestsFunc


logger = logging.getLogger('root')


def version():
    return '2.2.0'

@app.before_request
def before_request():
    g.db = db
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


class Index(Resource):

    def get(self):
        return {'msg': "Welcome to use SX-CarRecgServer %s" % version()}

class RecgList(Resource):

    def post(self):
        """识别请求信息"""
        if not request.json:
            return {'package': None, 'msg': 'Bad Request', 'code': 101}, 400
        if request.json.get('key', None) not in gl.KEYSDICT:
            return {'package': None, 'msg': 'Key Error', 'code': 105}
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

        if gl.RECGQUE.qsize() > app.config['MAXSIZE']:
            return {'carinfo': None, 'msg': 'Server Is Busy', 'code': 108}

        gl.RECGQUE.put((10, request.json['info'],
                        request.json['key'], que))

        try:
            recginfo = que.get(timeout=5)
        except Queue.Empty:
            recginfo = {'carinfo': None, 'msg': 'Time Out', 'code': 107}
        finally:
            return recginfo


class StateList(Resource):

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('key', type=unicode, required=True,
                            help='A key value is require', location='json')
        args = parser.parse_args()

        if User.get_one(User.key == request.json['key']) is None:
            return {'status': 401, 'message': 'Unauthorized access'}, 401

        return {'carinfo': None, 'msg': 'State', 'code': 120,
                'state': {'threads': app.config['THREADS'],
                          'qsize': gl.RECGQUE.qsize()},
                'user': gl.KEYSDICT.get(request.json['key'])}


api.add_resource(Index, '/')
api.add_resource(RecgList, '/recg')
api.add_resource(StateList, '/state')

