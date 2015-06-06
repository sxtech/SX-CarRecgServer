# -*- coding: utf-8 -*-
import os


class Config(object):
    DEBUG = True
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    # 主机IP
    HOST = '0.0.0.0'
    # 数据库名称
    DATABASE = 'carrecgser.db'
    # 识别线程数
    THREADS = 4
    # 允许最大数队列为线程数16倍
    MAXSIZE = THREADS * 16
    PORT = '8060'
    # 图片下载文件夹
    IMG_PATH = 'img'
    # 图片截取文件夹
    CROP_PATH = 'crop'
    # 超时
    TIMEOUT = 5

class Develop(Config):
    pass

class Production(Config):
    DEBUG = False

