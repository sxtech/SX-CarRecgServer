# -*- coding: utf-8 -*-

from car_recg import Users, Recglist
from car_recg.carrecg import CarRecgEngine
#from car_recg import RequestsFunc
import json

def models_test():
    #for user in User.select():
    #    print user.key
    #print User.get_one(User.key == 'sx2767722_10')
    u = Users.get_one(Users.username == 'kakou')
    print u.password

def create_table():
    Users.create_table(True)
    Recglist.create_table(True)

def save_test():
    r = Recglist.create(timestamp=123,
                          imgurl='http://www.baidu.com',
                          recginfo='{"海贼王":123}')
    print r.last_insert_id()

def recg_test():
    r = CarRecgEngine()
    print r.imgrecg('test.jpg', [])
    del r

def get_test():
    for users in Users.select().where(Users.banned == 0):
        print users.id

if __name__ == '__main__':
    #models_test()
    #create_table()
    #save_test()
    #recg_test()
    get_test()
