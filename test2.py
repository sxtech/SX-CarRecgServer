from car_recg import User
from car_recg import RequestsFunc
import json

def models_test():
    for user in User.select():
        print user.key
    print User.get_one(User.key == 'sx2767722_10')

def requests_test():
    rf = RequestsFunc()
    url = 'http://127.0.0.1:8060/recg'
    json_data = {'imgurl':'http://localhost/imgareaselect/imgs/1.jpg','coordinates':None}
    data={'key':'sx2767722_10','info': json_data}
    r = rf.send_post(url,json.dumps(data))
    print r.text
    del rf

if __name__ == '__main__':
    requests_test()
