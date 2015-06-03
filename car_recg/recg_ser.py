# -*- coding: utf-8 -*-
import os

from app import app, logger
import gl
from recg_thread import RecgThread
from iniconf import MyIni


class RecgServer:
    def __init__(self):
        # 配置文件
        self.ini = MyIni()
        self.sysini = self.ini.get_sys_conf()

        app.config['THREADS'] = self.sysini['threads']
        # 创建图片下载文件夹
        if not os.path.exists(app.config['IMG_PATH']):
            os.makedirs(app.config['IMG_PATH'])
        # 创建图片截取文件夹
        if not os.path.exists(app.config['CROP_PATH']):
            os.makedirs(app.config['CROP_PATH'])

        logger.info('Recg server start')

    def __del__(self):
        del self.ini
        gl.IS_QUIT = True
        logger.info('Recg server quit')

    def main(self):
        # 创建车辆识别线程
        for i in range(app.config['THREADS']):
            RecgThread(i).start()
