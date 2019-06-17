#!/bin/python
# -*- coding: utf-8 -*-

import platform
import time
import os
import sqlite3

import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


SQLITE_FILE='offers.db'


class ByExt(By):
    ACTION = 'action'
    VALUE = 'value'
    CLASS = 'class'


class SKScrapper:

    def __init__(self, user, passwd, driver_path):

        self.user = user
        self.passwd = passwd
        self.driver_path = driver_path

        self.homepage = "https://www.slimmerkopen.nl"
        self.display = None
        self.driver = None

        self.headless = True 
        if not self.__is_linux():
            self.headless = False

    def __is_linux(self):
        return platform.system() == 'Linux'

    def start(self):
        if self.headless:
            self.__start_display()
        self.__start_driver()

    def __start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--kiosk")
        self.driver = webdriver.Chrome(self.driver_path, options=options)

    def __start_display(self):
        from pyvirtualdisplay import Display
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()

    def load_login_form(self):
        print('Getting page {}'.format(self.homepage))
        self.driver.get(self.homepage)
        self.wait_for(ByExt.ID, "headerBtnLogin")

    def login(self):
        print('Trying to get the login form')
        self.__find_one_by(ByExt.ID, "headerBtnLogin").click()
        login_form = self.__find_one_by(ByExt.ACTION, "https://www.slimmerkopen.nl/aanmelden")
        self.__find_one_from(login_form, ByExt.NAME, 'username').send_keys(self.user)
        self.__find_one_from(login_form, ByExt.NAME, 'password').send_keys(self.passwd)
        self.__scroll_to_the_bottom()
        self.__find_one_from(login_form, ByExt.VALUE, 'login').click()
        self.wait_for(ByExt.ID, "headerBtnSK")


    def find_and_sign_up_in_open_offers(self):
        print('Looking for open offers...')
        open_offers = []
        offers = self.driver.find_elements_by_class_name('respond')

        for offer in offers:
            if offer.text:
                open_offers.append(offer)
            offer.click()

        return open_offers

    def get_offer_info(self, offer):
        offer_info = {}
        advert = self.__find_parent_from(offer, ByExt.CLASS, 'advert')
        if advert:
            offer_info['area'] = self.__find_one_from(advert, ByExt.CLASS, 'area').text
            offer_info['discount'] = self.__find_one_from(advert, ByExt.CLASS, 'discount').text
            offer_info['price'] = self.__find_one_from(advert, ByExt.CLASS, 'price').text
            offer_info['description-smaller'] = self.__find_one_from(advert, ByExt.CLASS, 'description-smaller').text
        return offer_info

    def refresh(self):
        self.driver.refresh()

    def wait_for(self, how, element, timeout_secs=10):
        element =  WebDriverWait(self.driver, timeout=timeout_secs).until(
            EC.presence_of_element_located((how, element))
        )
        return element

    @staticmethod
    def __find_one_from(from_element, how, element_id):
        return from_element.find_element_by_xpath('//*[@{}="{}"]'.format(how, element_id))

    @staticmethod
    def __find_parent_from(from_element, how, element_id):
        while True:
            try:
                from_element = from_element.find_element(ByExt.XPATH, '..')
                if from_element.get_attribute(how) == element_id:
                    return from_element
            except Exception:
                return None

    def __find_one_by(self, how, element_id):
        return self.__find_one_from(self.driver, how, element_id)

    def __scroll_to_the_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def stop(self):
        print('stopping...')
        if self.headless:
            self.display.stop()
        self.driver.quit()
        print('stopped!')


def db_exists():
    return os.path.isfile(SQLITE_FILE)


def create_offers_db():
    conn = sqlite3.connect(SQLITE_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE offers(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                area VARCHAR(64),
                discount VARCHAR(64),
                price VARCHAR(64),
                description VARCHAR(64),
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)''')

    conn.commit()
    conn.close()


def save_offer_to_db(offer):
    try:
        conn = sqlite3.connect(SQLITE_FILE)
        c = conn.cursor()

        c.execute("INSERT INTO offers(area, discount, price, description) VALUES('{}','{}','{}','{}')"
                    .format(offer['area'], offer['discount'], offer['price'], offer['description-smaller']))

        conn.commit()
        conn.close()
    except:
        pass



def start_scrapper_with_credentials(user, passwd, driver_path):

    scrapper = SKScrapper(user, passwd, driver_path)
    scrapper.start()
    scrapper.load_login_form()
    scrapper.login()

    while True:
        new_offers = scrapper.find_and_sign_up_in_open_offers()

        if new_offers:
            print("Signed up in {} open offers: ".format(len(new_offers)))
            for offer in new_offers:
                offer_info = scrapper.get_offer_info(offer)
                save_offer_to_db(offer_info)
        else:
            print("No open offers found...")

        print('Refreshing...\n')
        scrapper.refresh()
        time.sleep(1)

    scrapper.stop()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", dest="user", action="store", required=True, help="SlimmerKopen user")
    parser.add_argument("-p", dest="passwd", action="store", required=True, help="SlimmerKopen password")
    parser.add_argument("-c", dest="chromedriver", action="store", required=True, help="Chromedriver binary path")
    args = parser.parse_args()

    if not db_exists():
        create_offers_db()

    start_scrapper_with_credentials(args.user, args.passwd, args.chromedriver)


if __name__ == "__main__":
    main()