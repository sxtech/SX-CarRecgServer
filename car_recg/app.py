# -*- coding: utf-8 -*-

from flask import Flask
from flask_restful import Api
from peewee import SqliteDatabase


# create a flask application - this ``app`` object will be used to handle
app = Flask(__name__)
api = Api(app)
app.config.from_pyfile('config.py')
db = SqliteDatabase(app.config['DATABASE'], journal_mode='WAL')
