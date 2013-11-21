#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/21/13 1:28 PM'


import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from .util import *


PhantomJS_UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
    'Chrome/28.0.1500.95 Safari/537.36'
LOGIN_URL = 'https://mp.weixin.qq.com/'


class AuthenticationFailed(Exception):
    pass


class OperationFailed(Exception):
    pass


class WeChatClient(object):
    def chrome_client(self):
        BIN_PATH = os.sep.join('bin/chromedriver'.split('/'))
        binary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), BIN_PATH)
        desired_capabilities = DesiredCapabilities.CHROME.copy()
        desired_capabilities['chrome.prefs'] = {
            "profile.managed_default_content_settings.images": 2,
        }
        self.driver = webdriver.Chrome(
            executable_path=binary_path,
        )

    def phantomJS(self):
        BIN_PATH = os.sep.join('bin/phantomjs'.split('/'))
        binary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), BIN_PATH)
        desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
        desired_capabilities['phantomjs.page.settings.userAgent'] = PhantomJS_UA
        service_args = [
            '--load-images=no',
        ]
        self.driver = webdriver.PhantomJS(
            desired_capabilities=desired_capabilities,
            executable_path=binary_path,
            service_args=service_args,
        )

    def __init__(self):
        self.phantomJS()
        self.waiter = WebDriverWait(self.driver, 10)

    def login(self, username, passwd):
        self.driver.get(LOGIN_URL)
        ID(self.driver, 'account').send_keys(username)
        ID(self.driver, 'password').send_keys(passwd)
        ID(self.driver, 'login_button').click()

        try:
            self.waiter.until(lambda driver: 'cgi-bin/home' in driver.current_url)
        except TimeoutException:
            raise AuthenticationFailed

        if 'cgi-bin/home' not in self.driver.current_url:
            raise AuthenticationFailed

    def list_users(self):
        href = CSS(self.driver, '#menu_contact a').get_attribute('href')
        self.driver.get(href)

        try:
            self.waiter.until(lambda driver: driver.current_url == href)
        except TimeoutException:
            raise OperationFailed

        users = CSS_N(self.driver, '.table_cell.user .user_info a.remark_name')
        self.user_list = {user.text: {
            'name': user.text,
            'page_url': user.get_attribute('href'),
        } for user in users}

        return self.user_list

    def send_message(self, name, message):
        page_url = self.user_list[name]['page_url']
        self.driver.get(page_url)

        try:
            self.waiter.until(lambda driver: driver.current_url == page_url)
        except TimeoutException:
            raise OperationFailed

        result = self.driver.execute_script("""
            var editor = $('.emotion_editor [contenteditable=true]');
            editor.text('%s');
            return editor.text();
            """ % message.replace("'", "\'"))

        text_area = CSS(self.driver, '.emotion_editor [contenteditable=true]')
        if text_area.text != message:
            raise OperationFailed

        text_area.send_keys(message)

        ID(self.driver, 'js_submit').click()

        if text_area.text != message:
            raise OperationFailed

        try:
            self.waiter.until(presence_of_element_located((By.CSS_SELECTOR, '.JS_TIPS.page_tips .inner')))
        except TimeoutException:
            raise OperationFailed

        if CSS(self.driver, '.JS_TIPS.page_tips .inner').text != u'回复成功':
            raise OperationFailed
