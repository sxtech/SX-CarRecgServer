# -*- coding: utf-8 -*-
import os
import logging
import Queue

from app import app, db
from models import User
import gl
from recg_thread import RecgThread
from iniconf import MyIni


logger = logging.getLogger('root')


class RecgServer:
    def __init__(self):
        # 配置文件
        self.ini = MyIni()
        self.sysini = self.ini.get_sys_conf()
        self.centreini = self.ini.get_ser_centre_conf()
        # 创建sqlite对象
        self.db = db
        # 识别消息优先队列
        gl.RECGQUE = Queue.PriorityQueue()

        app.config['THREADS'] = self.sysini['threads']

        # 创建图片下载文件夹
        if not os.path.exists(app.config['IMG_PATH']):
            os.makedirs(app.config['IMG_PATH'])
        # 创建图片截取文件夹
        if not os.path.exists(app.config['CROP_PATH']):
            os.makedirs(app.config['CROP_PATH'])

    def __del__(self):
        gl.IS_QUIT = True
        del self.ini

    def main(self):
        self.db.connect()
        for user in User.select():
            gl.KEYSDICT[user.key] = {'priority': user.priority,
                                     'multiple': user.multiple}
        self.db.close()
        # 权限队列数
        gl.P_SIZE = {10: 0, 20: 0, 30: 0}
        # 创建车辆识别线程
        for c in range(app.config['THREADS']):
            RecgThread(c).start()

