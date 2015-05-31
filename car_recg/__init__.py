# -*- coding: utf-8 -*-
from app import app
from models import User, Users
import views
from requests_func import RequestsFunc
from recg_ser import RecgServer
from my_logger import debug_logging, online_logging
from iniconf import MyIni

__version__ = '2.3.0'

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
