# -*- coding: utf-8 -*-
import os
import time
import Queue
import logging
import threading

from app import app
import gl
from requests_func import RequestsFunc
from carrecg import CarRecgEngine

logger = logging.getLogger('root')


class RecgThread(threading.Thread):

    def __init__(self, _id):
        threading.Thread.__init__(self)
        # 识别线程ID
        self._id = _id
        # 创建识别引擎对象
        self.cre = CarRecgEngine()
        # HTTP客户端类对象
        self.rf = RequestsFunc()

    def __del__(self):
        del self.cre
        del self.rf

    def run(self):
        while 1:
            try:
                if gl.IS_QUIT:
                    break
                p, request, que = gl.RECGQUE.get(timeout=1)
            except Queue.Empty:
                pass
            except Exception as e:
                logger.error(e)
                time.sleep(1)
            else:
                recginfo = {}
                filename = os.path.join(app.config['IMG_PATH'],
                                        '%s.jpg' % str(self._id))
                try:
                    self.rf.get_url_img(request['imgurl'], filename)
                except Exception as e:
                    logger.error(e)
                    recginfo = {'carinfo': None,
                                'msg': 'Url Error',
                                'code': 103}
                else:
                    try:
                        carinfo = self.cre.imgrecg(filename, request['coord'])
                        if carinfo is None:
                            recginfo = {'carinfo': None,
                                        'msg': 'Recognise Error',
                                        'code': 102}
                            logger.error('Recognise Error')
                        elif carinfo['head']['code'] == 0:
                            recginfo = {'carinfo': None,
                                        'msg': 'Recg Server Error',
                                        'code': 109}
                        else:
                            recginfo = {'carinfo': carinfo['body'],
                                        'msg': 'Success',
                                        'code': 100}
                        os.remove(filename)
                    except Exception as e:
                        logger.exception(e)
                        recginfo = {'carinfo': None,
                                    'msg': 'Unknow Error',
                                    'code': 104}

                try:
                    que.put(recginfo)
                except Exception as e:
                    logger.exception(e)

