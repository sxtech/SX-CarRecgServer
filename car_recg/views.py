# -*- coding: utf-8 -*-
import os
import time
import json
import Queue
import random

from flask import g, request
from flask_restful import reqparse, Resource
from passlib.hash import sha256_crypt

from app import app, db, api, auth, logger
from models import Users, Recglist
import gl
from requests_func import get_url_img

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

        if app.config['RECGQUE'].qsize() > app.config['MAXSIZE']:
            return {'message': 'Server is busy'}, 403

        imgname = '%32x' % random.getrandbits(128)
        imgpath = os.path.join(app.config['IMG_PATH'], '%s.jpg' % imgname)
        try:
            get_url_img(request.json['imgurl'], imgpath)
        except Exception as e:
            logger.error('Error url: %s' % request.json['imgurl'])
            return {'message': 'Url Error'}, 403

        app.config['RECGQUE'].put((10, request.json, que, imgpath))

        try:
            recginfo = que.get(timeout=app.config['TIMEOUT'])

            os.remove(imgpath)
        except Queue.Empty:
            return {'message': 'Time out'}, 408
        except Exception as e:
            logger.error(e)
        else:
            return {'imgurl': request.json['imgurl'],
                    'coord': request.json['coord'],
                    'recginfo': recginfo}, 201


class StateListApiV1(Resource):

    @auth.login_required
    def get(self):
        return {'msg': 'State', 'code': 120,
                'threads': app.config['THREADS'],
                'qsize': gl.RECGQUE.qsize()}


api.add_resource(Index, '/')
api.add_resource(RecgListApiV1, '/v1/recg')
api.add_resource(StateListApiV1, '/v1/state')
