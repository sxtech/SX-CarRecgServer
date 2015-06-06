# -*- coding: utf-8 -*-
import logging

from flask import Flask
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth
from peewee import SqliteDatabase

from config import Production


# create a flask application - this ``app`` object will be used to handle
app = Flask(__name__)
config = Production()
app.config.from_object(config)
api = Api(app)

db = SqliteDatabase(app.config['DATABASE'], journal_mode='WAL')

auth = HTTPBasicAuth()

logger = logging.getLogger('root')
