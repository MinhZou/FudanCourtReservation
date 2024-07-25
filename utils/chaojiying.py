#!/usr/bin/env python
# coding:utf-8

import requests
from hashlib import md5


class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password =  password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def post_pic(self, im, codetype):
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def report_error(self, im_id):
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()

    def extract_coordinates(self, captcha_dic):
        string = captcha_dic['pic_str']
        string = string.strip("'")
        entries = string.split('|')
        result = {}
        for entry in entries:
            character, left, top = entry.split(',')
            result[character] = {'left': int(left), 'top': int(top)}
        return result

def get_captcha_results():
    # http://www.chaojiying.com/
    chaojiying = Chaojiying_Client('user', 'password', 'soft_id')
    # img = open('../a.png', 'rb').read()
    img = open('../full_image.png', 'rb').read()
    captcha_dic = chaojiying.post_pic(img, 9501)
    print(captcha_dic)
    print(type(captcha_dic))
    print(type(captcha_dic['pic_str']))
    return captcha_dic['pic_str']


# if __name__ == '__main__':
    # print(get_captcha_results())
	# im = open('a.jpg', 'rb').read()
	# print(chaojiying.PostPic(im, 1902))

