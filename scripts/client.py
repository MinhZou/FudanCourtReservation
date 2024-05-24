# -*- coding: utf-8 -*-
"""
@author: MinhZou
@date: 2022-04-03
@e-mail: 770445973@qq.com
"""

import os
import io
import sys
import re
import yaml
import json
import random
import time
import datetime
import logging
from bs4 import BeautifulSoup
from lxml import etree
import urllib.parse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from apscheduler.schedulers.blocking import BlockingScheduler
import multiprocessing
import threading
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import cv2


from utils import chaojiying, send_email, get_dis_from_captcha

logging.basicConfig(level=logging.INFO, format='[%(asctime)s - %(name)s - %(levelname)s - %(process)s - %(thread)s] %(message)s')

class Client(object):
    def __init__(self, configs):
        self.username = configs['username']
        self.password = configs['password']
        self.orderuser = configs['orderuser']
        self.mobile = configs['mobile']
        self.court_name = configs['court_name']
        self.email = configs['email']
        self.driver_path = './chromedriver/chromedriver_bak.exe'
        # self.time_end = time_end
        self.time_end = '23:59:59'

        self.cookie = ''
        self.cookie_dic = {}
        self.courts_dic = {
            '北区体育馆羽毛球(标场)':'2c9c486e4f821a19014f826f2a4f0036', 
            '北区体育馆羽毛球(非标场)': '000000005079fc7001507a0f09a2000e',
            '正大体育馆羽毛球(标场)': '2c9c486e4f821a19014f82418a900004',
            '正大体育馆羽毛球(非标场)': '2c9c486e4f821a19014f86df4f662ba9',
            '江湾体育馆羽毛球场':'8aecc6ce749544fd01749a31a04332c2',
            '北区体育馆排球':'2c9c486e4f821a19014f827298da0047',
            '江湾体育馆网球场':'8aecc6ce7176eb18017225bfcd292809',
            '江湾室外网球场':'8aecc6ce780fe18301786c51f2a5627b',
            '江湾体育馆排球场': '8aecc6ce7176eb18017225c2e7d62831'
            }
        self.content_id = self.courts_dic[self.court_name]
        self.category_id = '2c9c486e4f821a19014f82381feb0001'
        self.count_var = multiprocessing.Value('i', 0)
        self.resource_dic = multiprocessing.Manager().dict()
        self.status_dic = multiprocessing.Manager().dict()
        self.reserved_dic = multiprocessing.Manager().dict()
        self.today_date = datetime.datetime.now().strftime("%Y-%m-%d") # '2022-03-20'
        self.search_date = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        self.time_scheduled = datetime.datetime.strptime('{} {}'.format(self.today_date, self.time_end), '%Y-%m-%d %H:%M:%S')
        # self.logger = log.get_logger('logs', name='client') logging not support multiprocess

        # Use to recognize the Verification Code (http://www.chaojiying.com/).
        self.cjy_usrname = '###' # 账户
        self.cjy_password = '###' # 密码
        self.cjy_soft_id = '###' # 接口id

        # Preseted time order
        # self.stage_1 = ['20:00', '19:00', '18:00']
        self.stage_1 = configs['stage_1']
        # self.stage_1 = ['14:00', '15:00', '16:00']
        self.stage_2 = ['17:00', '16:00', '15:00']
        self.stage_3 = ['11:00', '10:00', '09:00']

        #
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                          '(KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'

    def get_cookie_by_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        s = Service(r'{}'.format(self.driver_path))
        # browser = webdriver.Chrome(service=s)
        browser = webdriver.Chrome(service=s,options=chrome_options)
        browser.get("https://uis.fudan.edu.cn/authserver/login?service=https%3A%2F%2Felife.fudan.edu.cn%2Flogin2.action")
        time.sleep(5)
        browser.find_element(By.ID,"username").send_keys("{}".format(self.username))
        browser.find_element(By.ID,"password").send_keys("{}".format(self.password))
        logging.info('成功填充账号和密码！！！')
        time.sleep(2)
        browser.find_element(By.ID,"idcheckloginbtn").click()
        time.sleep(6)
        cookie_items = browser.get_cookies()
        cookie_str = ''
        for item_cookie in cookie_items:
            item_str = item_cookie["name"]+"="+item_cookie["value"]+"; "
            cookie_str += item_str
        browser.quit()
        if 'iPlanetDirectoryPro' in cookie_str:
            logging.info('成功获取cookie！！！')
            logging.info(cookie_str)
            self.cookie = cookie_str
            cookie_lst = self.cookie.split(';')
            for c_item in cookie_lst:
                c = c_item.strip()
                c_new = c.split('=')
                if len(c_new) == 2:
                    self.cookie_dic[c_new[0]] = c_new[1]
        return cookie_str

    def get_resource(self):
        resource_url = 'https://elife.fudan.edu.cn/public/front/getResource2.htm?' \
                       'contentId={}&ordersId=&currentDate={}'.format(self.content_id, self.search_date)
        headers = {
            'cookie': self.cookie,
            'referer': 'https://elife.fudan.edu.cn/public/front/toResourceFrame.htm?contentId={}'.format(self.content_id),
            'user-agent': self.user_agent,
            'Connection': 'close'
        }
        try:
            logging.info('获取ID中...')
            resource_resp = requests.get(resource_url, headers=headers)
            html_resource = resource_resp.text
            # print(html_resource)
            soup = BeautifulSoup(html_resource,'html.parser')
            table = soup.find("table", "site_table")
            for line in table.findAll('tr'):
                resource_item = line.find('img',style="cursor:pointer")
                if resource_item:
                    begin_time = line.find('td', 'site_td1').text[:5]
                    onclick = resource_item.attrs['onclick']
                    resource_id = re.findall(r"'(.*?)'", onclick)[0]
                    self.resource_dic[begin_time] = resource_id
            resource_resp.close()
        except Exception as e:
            # logger.error('Faild to get result', exc_info=True)
            logging.info(str(e))
            time.sleep(5)
            self.cookie = self.get_cookie_by_selenium()
        return

    def get_captcha_img(self, resource_id):
        timestamp_ms = int(time.time() * 1000)
        # print(timestamp_ms)
        img_code_url = 'https://elife.fudan.edu.cn/public/front/getImgSwipe.htm?_={}'.format(timestamp_ms)
        img_code_headers = {
            'cookie': self.cookie,
            'user-agent': self.user_agent,
            'Connection': 'close'
        }
        img_code_resp = requests.get(img_code_url, headers=img_code_headers)
        src_image = ''
        if img_code_resp.status_code == 200:
            data = img_code_resp.json()
            SrcImage = "data:image/jpg;base64," + data['object']['SrcImage']
            src_image = data['object']['SrcImage']
            CutImage = "data:image/jpg;base64," + data['object']['CutImage']
            YPosition = data['object']['YPosition']
            SrcImageWidth = data['object']['SrcImageWidth']
            SrcImageHeight = data['object']['SrcImageHeight']
            # call imgVer() function with extracted properties here
        else:
            print("Request failed with status code: ", img_code_resp.status_code)
        # print(img_code_resp.json())
        img_code_resp.close()
        # print(src_image)
        return src_image

    def get_src_cut_img(self, resource_id):
        timestamp_ms = int(time.time() * 1000)
        # print(timestamp_ms)
        img_code_url = 'https://elife.fudan.edu.cn/public/front/getImgSwipe.htm?_={}'.format(timestamp_ms)
        img_code_headers = {
            'cookie': self.cookie,
            'user-agent': self.user_agent,
            'Connection': 'close'
        }
        img_code_resp = requests.get(img_code_url, headers=img_code_headers)
        src_image = ''
        cut_img = ''
        if img_code_resp.status_code == 200:
            data = img_code_resp.json()
            SrcImage = "data:image/jpg;base64," + data['object']['SrcImage']
            src_image = data['object']['SrcImage']
            CutImage = "data:image/jpg;base64," + data['object']['CutImage']
            cut_img = data['object']['CutImage']
            YPosition = data['object']['YPosition']
            SrcImageWidth = data['object']['SrcImageWidth']
            SrcImageHeight = data['object']['SrcImageHeight']
            # call imgVer() function with extracted properties here
        else:
            print("Request failed with status code: ", img_code_resp.status_code)
        img_code_resp.close()
        return src_image, cut_img


    def get_captcha_results(self, base64_data):
        byte_data = base64.b64decode(base64_data)
        dis, wbili = get_dis_from_captcha.get_dis_cv(byte_data)
        return dis, wbili

    def get_src_cut_results(self, bg_base64_data, bl_base64_data):
        bg_byte_data = base64.b64decode(bg_base64_data)
        bl_byte_data = base64.b64decode(bl_base64_data)
        dis, wbili = get_dis_from_captcha.get_dis_bg_bl(bg_byte_data, bl_byte_data)
        return dis, wbili


    def get_order_page_by_selenium(self, resource_id):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        s = Service(r'{}'.format(self.driver_path))
        # browser = webdriver.Chrome(service=s)
        browser = webdriver.Chrome(service=s,options=chrome_options)
        order_page_url = 'https://elife.fudan.edu.cn/public/front/loadOrderForm_ordinary.htm?' \
                         'serviceContent.id={}&serviceCategory.id={}&codeStr=&resourceIds={}&orderCounts=1'.format(self.content_id, self.category_id, resource_id)
        browser.get(order_page_url)
        for key, val in self.cookie_dic.items():
            c_dic = {"name": key, "value": val}
            browser.add_cookie(c_dic)
        browser.get(order_page_url)
        browser.refresh()
        verify_button = browser.find_element_by_css_selector('#verify_button')
        verify_button.click()
        time.sleep(0.1)

        base64_str = browser.find_element_by_css_selector('#scream').get_attribute('src')
        browser.quit()

        # print(base64_str) # data:image/jpg;base64,
        base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
        # print(base64_data)
        byte_data = base64.b64decode(base64_data)
        dis, wbili = get_dis_from_captcha.get_dis_cv(byte_data)
        print(dis, wbili)
        return dis, wbili


    def post_order(self, resource_id, moveEnd_X, wbili):
        post_url = 'https://elife.fudan.edu.cn/public/front/saveOrder.htm?op=order'
        post_headers = {
            'cookie': self.cookie,
            'referer': 'https://elife.fudan.edu.cn/public/front/loadOrderForm_ordinary.htm?serviceContent.id='
                       '{}&serviceCategory.id={}&codeStr=&resourceIds={}&orderCounts=1'.format(self.content_id, self.category_id, resource_id),
            'user-agent': self.user_agent,
            'Connection': 'close'
        }
        data_form = {
            'moveEnd_X': moveEnd_X,
            'wbili': wbili,
            'serviceContent.id': self.content_id,
            'serviceCategory.id': self.category_id,
            'contentChild': '',
            'codeStr':'',
            'itemsPrice': '',
            'acceptPrice': '',
            'orderuser': self.orderuser,
            'resourceIds': resource_id,
            'orderCounts': '1',
            'lastDays': '0',
            'mobile': self.mobile,
            'd_cgyy.bz': ''
        }
        post_resp = requests.post(url=post_url, data=data_form, headers=post_headers)
        post_resp.close()
        return post_resp


    def get_status(self):
        status_url = 'https://elife.fudan.edu.cn/public/userbox/index.htm?userConfirm=&orderstateselect='
        headers = {
            'cookie': self.cookie,
            'referer': 'https://elife.fudan.edu.cn/public/userbox/index2.htm',
            'user-agent': self.user_agent,
            'Connection': 'close',
        }

        resource_resp = requests.get(status_url, headers=headers)
        html_resource = resource_resp.text
        soup = BeautifulSoup(html_resource,'html.parser')
        try:
            table = soup.find("table", "table3")
            for line in table.findAll('tr'):
                status_item = line.findAll('td')
                if '待签到' in status_item[5].text:
                    onclick = status_item[6].find('a').attrs['onclick']
                    order_id = re.findall(r"'(.*?)'", onclick)[0]
                    status_key = status_item[3].text[-5:] + '-' + status_item[4].text[:5]
                    self.status_dic[status_key] = order_id
        except Exception as e:
            logging.info(e)
        resource_resp.close()
        logging.info('已预定{}'.format(self.status_dic))
        return

    def cancel_reservation(self, search_date, time):
        order_id = self.status_dic[self.search_date + '-' + time]
        cancel_url = 'https://elife.fudan.edu.cn/public/userbox/canCancel.htm?orderid={}'.format(order_id)
        cancel_headers = {
            'cookie': self.cookie,
            'referer': 'https://elife.fudan.edu.cn/public/userbox/index.htm?userConfirm=&orderstateselect=',
            'user-agent': self.user_agent,
            'Connection': 'close',
        }

        data_form = {
            'pageNo': '',  
            'orderdate': '', 
            'orderstateselect': '', 
            'userConfirm': '0',
            'orderId': '', 
        }

        cancel_get_url = 'https://elife.fudan.edu.cn/public/userbox/cancelMyself.htm?orderid={}'.format(order_id)
        post_resp = requests.post(url=cancel_url, data=data_form, headers=cancel_headers)
        get_resp = requests.get(url=cancel_get_url, headers=cancel_headers)
        post_resp.close()
        get_resp.close()
        return post_resp

    def book_court(self, order_time, time_str):
        resource_id = self.resource_dic[order_time]
        logging.info('正在预定{}-{} {}'.format(self.court_name, self.search_date, order_time))
        src_img, cut_img = self.get_src_cut_img(resource_id)
        dis, wbili = self.get_src_cut_results(src_img, cut_img)
        dis, wbili = self.get_captcha_results(src_img)


        count = 1
        while True:
            self.get_status()
            key = self.search_date[-5:] + '-' + order_time
            logging.info(self.status_dic)
            logging.info(key)
            if key in self.status_dic:
                self.reserved_dic[order_time] = 1
                now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                flag = send_email.send_mail(now_time, time_str, self.court_name, self.username, self.email)
                if flag:
                    logging.info('邮件发送成功！')
                else:
                    logging.info('邮件发送失败！')
                break
            else:
                time.sleep(1)
                # logging.info('长度为{}：{}'.format(len(resp_txt), resp_txt))
                logging.info('第{}次重新预定{}-{} {}'.format(count, self.court_name, self.search_date, order_time))
                # dis, wbili = self.get_order_page_by_selenium(resource_id)
                src_img, cut_img = self.get_src_cut_img(resource_id)
                dis, wbili = self.get_src_cut_results(src_img, cut_img)
                dis, wbili = self.get_captcha_results(src_img)
                count += 1
                if count >= 3:
                    break
        return

    def single_job(self, order_time):
        self.today_date = datetime.datetime.now().strftime("%Y-%m-%d") # '2022-03-20'
        self.search_date = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        # self.time_scheduled = datetime.datetime.strptime('{} {}'.format(self.today_date, self.time_end), '%Y-%m-%d %H:%M:%S')
        self.time_scheduled = datetime.datetime.now() + datetime.timedelta(minutes=5, seconds=40)
        # ******************************************************************************************
        logging.info('*********************************Settings******************************')
        logging.info('预定人: {}'.format(self.orderuser))
        logging.info('手机号: {}'.format(self.mobile))
        logging.info('今天的日期: {}'.format(self.today_date))
        logging.info('预定的日期: {}'.format(self.search_date))
        logging.info('预定的场地：{}'.format(self.court_name))
        logging.info('预定的时间段：{}'.format(self.stage_1))
        logging.info('已预约的时间段：{}'.format(self.reserved_dic))
        logging.info('***********************************************************************')
        # ******************************************************************************************

        try:
            self.cookie = self.get_cookie_by_selenium()
        except Exception as e:
            logging.info(str(e))
            time.sleep(5 + 2*random.random())
            self.cookie = self.get_cookie_by_selenium()

        while 'iPlanetDirectoryPro' not in self.cookie:
            logging.info('cookie获取失败，重新获取...')
            time.sleep(5 + 2*random.random())
            self.cookie = self.get_cookie_by_selenium()

        while True:
            self.get_status()
            self.count_var.value = len(self.status_dic)
            if self.count_var.value >= 2:
                break
            now_time = datetime.datetime.now()
            if (now_time - self.time_scheduled).total_seconds() > 0:
                break
            try:
                if not self.resource_dic:
                    logging.info('{} {} 无场地可约'.format(self.court_name, self.search_date))
                    # resource_jobs = []
                    for _ in range(2):
                        t = threading.Thread(target=self.get_resource, args=())
                        t.setDaemon(True)
                        t.start()
                        time.sleep(0.4)
                    if (datetime.datetime.now() - (self.time_scheduled - datetime.timedelta(minutes=1, seconds=40))).total_seconds() > 0:
                        time.sleep(1 + 0.8*random.random())
                    else:
                        time.sleep(4 + 2*random.random())
                else:
                    for key, val in self.resource_dic.items():
                        logging.info('{}-{} {} 可约, ID为{}'.format(self.court_name, self.search_date, key, val))
                    if self.count_var.value >= 3:
                        break
                    time_str = self.search_date + ' ' + order_time
                    now_time = datetime.datetime.now()
                    if order_time in self.resource_dic and order_time not in self.reserved_dic.keys():
                        self.book_court(order_time, time_str)
                    elif order_time in self.reserved_dic.keys():
                        logging.info("已经预定 {}-{} {}".format(self.court_name, self.search_date, order_time))
                        break
                    else:
                        logging.info("不可约 {}-{} {}".format(self.court_name, self.search_date, order_time))
                        for _ in range(1):
                            t = threading.Thread(target=self.get_resource, args=())
                            t.setDaemon(True)
                            t.start()
                        time.sleep(5 + 2*random.random())
            except Exception as e:
                logging.info(str(e))
                time.sleep(5)
                self.cookie = self.get_cookie_by_selenium()

    def scheduled_job(self):
        my_jobs = []
        for order_time in self.stage_1:
            p = multiprocessing.Process(target=self.single_job, args=(order_time,))
            my_jobs.append(p)
            time.sleep(3)
            p.start()

        # # other time
        # time.sleep(190)
        # for order_time in self.stage_2:
        #     if self.count_var.value < 3:
        #         p = multiprocessing.Process(target=self.single_job, args=(order_time,))
        #         my_jobs.append(p)
        #         time.sleep(0.1)
        #         p.start()

        # time.sleep(10)
        # for order_time in self.stage_3:
        #     if self.count_var.value < 3:
        #         p = multiprocessing.Process(target=self.single_job, args=(order_time,))
        #         my_jobs.append(p)
        #         time.sleep(0.1)
        #         p.start()
        for p in my_jobs:
            p.join()

