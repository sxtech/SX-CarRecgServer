# -*- coding: utf-8 -*-
import os
import Queue


class Config(object):
    DEBUG = True
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    # 主机IP string
    HOST = '0.0.0.0'
    # 端口 string
    PORT = '8060'
    # 数据库名称 string
    DATABASE = 'carrecgser.db'
    # 识别线程数 int
    THREADS = 4
    # 允许最大数队列为线程数16倍 int
    MAXSIZE = THREADS * 16
    # 图片下载文件夹 string
    IMG_PATH = 'img'
    # 图片截取文件夹 string
    CROP_PATH = 'crop'
    # 超时 int
    TIMEOUT = 5
    # 识别优先队列 object
    RECGQUE = Queue.PriorityQueue()
    # 退出标记 bool
    IS_QUIT = False
    # 用户字典 dict
    USER = {}
    # 上传文件保存路径 string
    UPLOAD_PATH = 'upload'


class Develop(Config):
    pass


class Production(Config):
    DEBUG = False
