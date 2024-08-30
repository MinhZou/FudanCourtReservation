# -*- coding: utf-8 -*-
"""
Use to book sports venues on the Fudan campus
@author: MinhZou
@date: 2022-04-03 update 2024-07-25
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import multiprocessing
import threading
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import cv2
from utils.chaojiying import Chaojiying_Client
from selenium.webdriver.common.action_chains import ActionChains

from utils import send_email, image_process

logging.basicConfig(level=logging.INFO, format='[%(asctime)s - %(name)s - %(levelname)s - %(process)s - %(thread)s] %(message)s')


class Client(object):
    def __init__(self, configs):
        self.username = configs['username']
        self.password = configs['password']
        self.orderuser = configs['orderuser']
        self.mobile = configs['mobile']
        self.court_name = configs['court_name']
        self.email = configs['email']
        self.driver_path = './chromedriver/chromedriver.exe'
        # self.time_end = time_end
        self.time_end = '23:59:59'

        self.cookie = ''
        self.cookie_dic = {}
        self.courts_dic = {
            # '江湾体育馆网球场':'8aecc6ce7176eb18017225bfcd292809',
            # '江湾体育馆排球场': '8aecc6ce7176eb18017225c2e7d62831',
            '张江校区网球场': '8aecc6ce8ee75f34018f047dc8ca407a',
            '杨詠曼楼琴房': '8aecc6ce7bc2eea5017bed81312c5f49',
            '张江校区食堂三楼羽毛球(非标)': '8aecc6ce7641d43101764ac0e3c1524d',
            '江湾体育馆羽毛球场':'8aecc6ce749544fd01749a31a04332c2',
            '江湾体育馆室内网球': '8aecc6ce90ae440c0191458edad81857',
            '江湾体育馆篮球场(半场)': '8aecc6ce7176eb18017225c1505f2819',
            '江湾体育馆排球场1号': '8aecc6ce878581d701879c7548c6737d',
            '江湾体育馆排球场2号': '8aecc6ce7176eb18017225c2e7d62831',
            '江湾室外网球场':'8aecc6ce780fe18301786c51f2a5627b',
            '正大体育馆羽毛球(标场)': '2c9c486e4f821a19014f82418a900004',
            '正大体育馆羽毛球(非标场)': '2c9c486e4f821a19014f86df4f662ba9',
            '南区国权路网球场': '8aecc6ce7d2dffbd017de9ea4e7e4ece',
            '南区网球场': '8aecc6ce6b6e6698016bc5dc173c11b7',
            '邯郸路足球场': '2c9c486e4f821a19014f8266341f002f',
            '北区体育馆羽毛球(标场)':'2c9c486e4f821a19014f826f2a4f0036', 
            '北区体育馆羽毛球(非标场)': '000000005079fc7001507a0f09a2000e',
            '北区体育馆篮球': '2c9c486e4f821a19014f82706dfb003c',
            '北区体育馆排球':'2c9c486e4f821a19014f827298da0047',
            '北区体育馆舞蹈房(二楼)': '2c9c486e4f821a19014f82746a000052',
            '北区体育馆舞蹈房(三楼)': '2c9c486e4f821a19014f82754b190058', 
            '枫林学生活动中心三楼羽毛球馆': '8aecc6ce66f1173501675d11508e75eb',
            '枫林综合体育馆篮球(半场)': '8aecc6ce66f117350167070ac2393bca', 
            '枫林综合体育馆排球场': '8aecc6ce8672f0cd01869b1151d540f3',
            '北区体育馆乒乓球': '8aecc6ce8d17fc0e018e50bc62d0332b',
            '南区体育馆乒乓球': '8aecc6ce8d17fc0e018e50c24f3a3367', 
            '枫林学生活动中心乒乓球': '8aecc6ce8d17fc0e018e50cafd7b33b8',
            '张江学生活动中心乒乓球': '8aecc6ce8d17fc0e018e50d1a00633f1', 
            '江湾体育馆乒乓球场': '8aecc6ce8ee75f34018eeef359057431',
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
        self.cjy_usrname = '###'
        self.cjy_password = '###'
        self.cjy_soft_id = '###'
        self.Chaojiying_Client = Chaojiying_Client(self.cjy_usrname, self.cjy_password, self.cjy_soft_id)

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

    def get_captcha_image_and_valid_text(self, browser):
        try:
            img_selector = "img.valid_bg-img"
            valid_text_selector = "span.valid_tips__text"
            wait = WebDriverWait(browser, 5)  # 等待最多5秒
            img_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, img_selector)))
            valid_tips_text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, valid_text_selector)))
            valid_text = valid_tips_text.text.split("请依次点击：")[-1]
            print(f"Successfully retrieved valid text: {valid_text}")
            base64_str = img_element.get_attribute('src')
            if base64_str:
                captcha_image = image_process.base64_to_image(base64_str)
            else:
                captcha_image = None
        except Exception as e:
            print(f"An error occurred: {e}")
            valid_text = None
            captcha_image = None
        return captcha_image, valid_text

    def get_captcha_results(self, captcha_image):
        if captcha_image:
            res_dic = self.Chaojiying_Client.post_pic(captcha_image, 9501)
            captcha_dic = self.Chaojiying_Client.extract_coordinates(res_dic)
        else:
            captcha_dic = None
        return captcha_dic

    def click_captcha(self, browser, valid_text, captcha_dic):
        captcha_element = browser.find_element(By.CLASS_NAME, 'valid_bg-img')

        def replace_similar_chars(s, d):
            for char in s:
                matches = sum(1 for k in d if k == char)
                if matches >= 3:
                    for k in list(d.keys()):
                        if k == char:
                            d[char] = d.pop(k)
            return d

        # 文字识别不准确，手动调整，减少retry次数
        if len(valid_text) == len(captcha_dic) == 4:
            replace_similar_chars(valid_text, captcha_dic)

        if valid_text and captcha_dic:
            for _, valid_word in enumerate(valid_text):
                left = captcha_dic.get(valid_word, {}).get('left', 50)  # - 10
                top = captcha_dic.get(valid_word, {}).get('top', 50)  # - 20
                actions = ActionChains(browser)
                actions.move_to_element_with_offset(captcha_element, left, top).click().perform()
                time.sleep(0.5)
        return

    def get_order_page_by_selenium(self, resource_id):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        s = Service(r'{}'.format(self.driver_path))
        # browser = webdriver.Chrome(service=s)
        browser = webdriver.Chrome(service=s, options=chrome_options)
        order_page_url = 'https://elife.fudan.edu.cn/public/front/loadOrderForm_ordinary.htm?' \
                         'serviceContent.id={}&serviceCategory.id={}&codeStr=&resourceIds={}&orderCounts=1'.format(self.content_id, self.category_id, resource_id)
        browser.get(order_page_url)
        for key, val in self.cookie_dic.items():
            c_dic = {"name": key, "value": val}
            browser.add_cookie(c_dic)
        browser.get(order_page_url)
        # browser.refresh()
        time.sleep(5)

        try:
            verify_button = browser.find_element_by_css_selector('#verify_button1')
            verify_button.click() #
            time.sleep(1)
        except Exception as e:
            logging.info('Faild to click verify_button', exc_info=True)
            browser.quit()
            return

        captcha_image, valid_text = self.get_captcha_image_and_valid_text(browser)
        captcha_dic = self.get_captcha_results(captcha_image)
        print(f"Successfully retrieved captcha results: {captcha_dic}")
        # # Test
        # valid_text = "农务民息"
        # captcha_dic = {'务': {'left': 285, 'top': 129}, '息': {'left': 197, 'top': 127},
        #                '民': {'left': 121, 'top': 102}, '农': {'left': 56, 'top': 81}}
        self.click_captcha(browser, valid_text, captcha_dic)

        max_tries = 3
        time.sleep(1)
        for i in range(max_tries):
            value = None
            try:
                input_element = browser.find_element(By.ID, 'validateCode')
                value = input_element.get_attribute('value')
            except Exception as e:
                print("Error:", e)
            if value:
                print("Verification passed!")
                break
            else:
                print("Verification failed!")
                print("Retrying...")
                time.sleep(3)
                captcha_image, valid_text = self.get_captcha_image_and_valid_text(browser)
                captcha_dic = self.get_captcha_results(captcha_image)
                print(f"Successfully retrieved captcha results: {captcha_dic}")
                # # Test
                # valid_text = "农务民息"
                # captcha_dic = {'务': {'left': 285, 'top': 129}, '息': {'left': 197, 'top': 127},
                #                '民': {'left': 121, 'top': 102}, '农': {'left': 56, 'top': 81}}
                self.click_captcha(browser, valid_text, captcha_dic)
                time.sleep(1)

        try:
            element = browser.find_element_by_id('btn_sub')
            browser.execute_script("arguments[0].click();", element)
        except Exception as e:
            print("=======")
            raise
        browser.quit()
        return

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
        self.get_order_page_by_selenium(resource_id)

        count = 1
        while True:
            self.get_status()
            # if len(updated_status) > self.status_dic:
            #     self.status_dic = updated_status
            # status_dic = self.get_status()
            key = self.search_date[-5:] + '-' + order_time
            logging.info(self.status_dic)
            logging.info(key)
            if key in self.status_dic:
                # logging.info('长度为{}：{}'.format(len(resp_txt), resp_txt))
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
                self.get_order_page_by_selenium(resource_id)
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
            # updated_status = self.get_status(self.cookie)
            # if len(updated_status) > self.status_dic:
            #     self.status_dic = updated_status
            # key = search_date[-5:] + '-' + order_time
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

