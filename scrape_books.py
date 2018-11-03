#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 22:59:37 2018

@author: Constantin Kraft <ckraft@smail.uni-koeln.de>
"""

import os
from collections import namedtuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class NoLogin(Exception):
    pass


Book = namedtuple("Book", ["title", "author", "download_link"])

user = os.environ.get('PACKT_USER')
pw = os.environ.get('PACKT_PW')

if None in (user, pw):
    raise NoLogin("PacktPub credentials missing. Populate PACKTPUB_USER and PACKTPUB_PW in .env file or set them on "
                  "your shell.")

options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": os.path.realpath(os.path.join(os.path.dirname(__file__), 'books')),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

LOGIN_URL = 'https://www.packtpub.com/login'

driver = webdriver.Chrome(options=options)
driver.get(LOGIN_URL)

driver.find_element_by_id('edit-name').send_keys(user)
driver.find_element_by_id('edit-pass').send_keys(pw + Keys.RETURN)

books = []
LINK_TEXT = 'My eBooks'

try:
    # "My eBooks" page
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, LINK_TEXT)))
    button.click()

    wait.until(EC.presence_of_element_located((By.ID, "product-account-list")))
    book_elements = driver.find_elements(By.CLASS_NAME, "product-line")
    css_download_links = ".product-line .download-container a"
    # get only PDF download links
    # commented-out XPath 2.0 version
    # xpath_download_links = "//div[@class='download-container cf']/a[ends-with(@href, 'pdf')]"
    XPATH_DOWNLOAD_LINKS = "//div[contains(@class, 'download-container cf')]/a[substring(@href, string-length(@href) - \
string-length('pdf') +1) = 'pdf']"
    download_links = [e.get_attribute('href')
                      for e in driver.find_elements_by_xpath(XPATH_DOWNLOAD_LINKS)]

    for el, link in zip(book_elements, download_links):
        books.append(Book(title=el.get_attribute('title'), author=el.find_element_by_class_name('author').text,
                          download_link=link))

    # download books
    for book in books:
        driver.get(book.download_link)
finally:
    driver.quit()
