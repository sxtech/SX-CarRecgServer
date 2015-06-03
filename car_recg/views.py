# -*- coding: utf-8 -*-
import Queue

from flask import g, request
from flask_restful import reqparse, Resource
from passlib.hash import sha256_crypt

from app import app, db, api, auth
from models import Users
import gl


@app.before_request
def before_request():
    g.db = db
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@auth.verify_password
def verify_password(username, password):
    user = Users.get_one(Users.username == username)
    if not user:
        return False
    return sha256_crypt.verify(password, user.password)


class Index(Resource):

    def get(self):
        return {'recg_url': 'http://localhost/v1/recg',
                'state_url': 'http://localhost/v1/state'}


class RecgListApiV1(Resource):

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('imgurl', type=unicode, required=True,
                            help='A jpg url is require', location='json')
        parser.add_argument('coord', type=list, required=True,
                            help='A coordinates array is require',
                            location='json')
        args = parser.parse_args()

        # 回调用的消息队列
        que = Queue.Queue()

        if gl.RECGQUE.qsize() > app.config['MAXSIZE']:
            return {'carinfo': None, 'msg': 'Server Is Busy', 'code': 108}, 202

        gl.RECGQUE.put((10, request.json, que))

        try:
            recginfo = que.get(timeout=app.config['TIMEOUT'])
        except Queue.Empty:
            recginfo = {'carinfo': None, 'msg': 'Time Out', 'code': 107}, 202
        finally:
            return recginfo


class StateListApiV1(Resource):

    @auth.login_required
    def get(self):
        return {'msg': 'State', 'code': 120,
                'threads': app.config['THREADS'],
                'qsize': gl.RECGQUE.qsize()}


api.add_resource(Index, '/')
api.add_resource(RecgListApiV1, '/v1/recg')
api.add_resource(StateListApiV1, '/v1/state')
