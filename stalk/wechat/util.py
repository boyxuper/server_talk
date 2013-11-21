# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '5/11/13 6:41 PM'

CSS = lambda driver, *args: driver.find_element_by_css_selector(*args)
CSS_N = lambda driver, *args: driver.find_elements_by_css_selector(*args)

NAME = lambda driver, *args: driver.find_element_by_name(*args)
NAME_N = lambda driver, *args: driver.find_elements_by_name(*args)

ID = lambda driver, *args: driver.find_element_by_id(*args)
ID_N = lambda driver, *args: driver.find_elements_by_id(*args)

XPATH = lambda driver, *args: driver.find_element_by_xpath(*args)
XPATH_N = lambda driver, *args: driver.find_elements_by_xpath(*args)

TAG = lambda driver, *args: driver.find_element_by_tag(*args)
TAG_N = lambda driver, *args: driver.find_elements_by_tag(*args)
