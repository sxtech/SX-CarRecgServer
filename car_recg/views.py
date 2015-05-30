# -*- coding: utf-8 -*-
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
    return '2.3.0'

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
        parser = reqparse.RequestParser()

        parser.add_argument('key', type=unicode, required=True,
                            help='A key value is require', location='json')
        parser.add_argument('url', type=unicode, required=True,
                            help='A jpg url is require', location='json')
        parser.add_argument('coordinates', type=list, required=True,
                            help='A coordinates array is require',
                            location='json')
        args = parser.parse_args()

        if User.get_one(User.key == request.json['key']) is None:
            return {'status': 401, 'message': 'Unauthorized access'}, 401

        # 回调用的消息队列
        que = Queue.Queue()

        if gl.RECGQUE.qsize() > app.config['MAXSIZE']:
            return {'carinfo': None, 'msg': 'Server Is Busy', 'code': 108}, 202

        gl.RECGQUE.put((10, request.json['info'],
                        request.json['key'], que))

        try:
            recginfo = que.get(timeout=5)
        except Queue.Empty:
            recginfo = {'carinfo': None, 'msg': 'Time Out', 'code': 107}, 202
        finally:
            return recginfo

class RecgListApiV1(Resource):

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('key', type=unicode, required=True,
                            help='A key value is require', location='json')
        parser.add_argument('url', type=unicode, required=True,
                            help='A jpg url is require', location='json')
        parser.add_argument('coordinates', type=list, required=True,
                            help='A coordinates array is require',
                            location='json')
        args = parser.parse_args()

        if User.get_one(User.key == request.json['key']) is None:
            return {'status': 401, 'message': 'Unauthorized access'}, 401

        # 回调用的消息队列
        que = Queue.Queue()

        if gl.RECGQUE.qsize() > app.config['MAXSIZE']:
            return {'carinfo': None, 'msg': 'Server Is Busy', 'code': 108}, 202

        gl.RECGQUE.put((10, request.json, que))

        try:
            recginfo = que.get(timeout=5)
        except Queue.Empty:
            recginfo = {'carinfo': None, 'msg': 'Time Out', 'code': 107}, 202
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
                'threads': app.config['THREADS'],
                'qsize': gl.RECGQUE.qsize()}


api.add_resource(Index, '/')
api.add_resource(RecgList, '/recg')
api.add_resource(StateList, '/state')
api.add_resource(RecgListApiV1, '/v1/recg')

