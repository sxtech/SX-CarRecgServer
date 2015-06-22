# -*- coding: utf-8 -*-
import time
import Queue
import threading

from app import app, logger
from carrecg import CarRecgEngine


class RecgThread(threading.Thread):

    def __init__(self, _id):
        threading.Thread.__init__(self)
        # 识别线程ID
        self._id = _id
        # 创建识别引擎对象
        self.cre = CarRecgEngine()

        logger.info('Recg thread %s start' % _id)

    def __del__(self):
        del self.cre
        logger.info('Recg thread %s quit' % self._id)

    def run(self):
        while 1:
            try:
                if app.config['IS_QUIT']:
                    break
                p, request, que, imgpath = app.config['RECGQUE'].get(timeout=1)
            except Queue.Empty:
                pass
            except Exception as e:
                logger.error(e)
                time.sleep(1)
            else:
                try:
                    carinfo = self.cre.imgrecg(imgpath, request['coord'])
                    if carinfo is None:
                        result = None
                        logger.error('Recognise Error')
                    elif carinfo['head']['code'] == 0:
                        result = None
                    else:
                        result = carinfo['body']
                except Exception as e:
                    logger.exception(e)
                    result = None
                try:
                    que.put(result)
                except Exception as e:
                    logger.error(e)
