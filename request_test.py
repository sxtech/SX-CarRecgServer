import json

import requests
from requests.auth import HTTPBasicAuth


def requests_test():
    url = 'http://127.0.0.1:8060/api/v1/recg'
    json_data = {'imgurl' : 'http://localhost/imgareaselect/imgs/1.jpg',
                 'coord' : []}
    r = requests.post(url, data=json.dumps(json_data),
                      headers={'content-type' : 'application/json'},
                      auth=HTTPBasicAuth('kakou', 'sx2767722'))
    print r.text, r.status_code

if __name__ == '__main__':
    requests_test()

