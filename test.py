from car_recg import User, Users
from car_recg import RequestsFunc
import json

def models_test():
    #for user in User.select():
    #    print user.key
    #print User.get_one(User.key == 'sx2767722_10')
    u = Users.get_one(Users.username == 'kakou')
    print u.password


if __name__ == '__main__':
    models_test()
