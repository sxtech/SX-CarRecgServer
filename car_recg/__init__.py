# -*- coding: utf-8 -*-
from app import app
from models import Users, Recglist
import views
from recg_ser import RecgServer
from my_logger import debug_logging, online_logging
from iniconf import MyIni

__version__ = '2.3.0'

'''
HTTP Status Code
200: OK
201: Created
400: Bad Request
401: Unauthorized
403: Forbidden
408: Request Timeout
422: Unprocessable Entity
449: Retry With
500: Internal Server Error
'''
