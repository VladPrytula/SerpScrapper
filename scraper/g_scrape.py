#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import abc
import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import codecs
from random import choice

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)


# NOTE: The next two sections are for demo purposes only, they will be imported from modules
# this will be stored in proxies.py module
# proxies = [
#     {'host': '1.2.3.4', 'port': '1234', 'username': 'myuser', 'password': 'pw'},
#     {'host': '2.3.4.5', 'port': '1234', 'username': 'myuser', 'password': 'pw'},
# ]
#
#
# def check_proxy(session, proxy_host):
#     response = session.get('http://canihazip.com/s')
#     returned_ip = response.text
#     if returned_ip != proxy_host:
#         raise StandardError('Proxy check failed: {} not used while requesting'.format(proxy_host))
#
#
# def random_proxy():
#     return choice(proxies)


class BaseScraper(object):
    def __init__(self):
        # TODO: this shoudl be grabbed from config
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        ]

    @abc.abstractmethod
    def scrape(self, f):
        """Retrieve data from the input source
           and return an object.
        """

    @abc.abstractmethod
    def make_query(self, query):
        """description here"""

    @abc.abstractmethod
    def save(self, data, out_file):
        """depending on the engine this shoudl be distinct"""

    def random_user_agent(self):
        return choice(self.user_agents)


class GoogleScraper(BaseScraper):
    def save(self, data, out_file):
        out_file.write(data + '\n')

    def make_query(self, query):
        return self.url_base + query.replace(" ", "+")

    @staticmethod
    def get_url(link):
        raw = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0]
        return raw[:raw.rfind(r"&sa=U")]

    def scrape(self, f):
        for query in tqdm(f):
            page = requests.get(self.make_query(query))
            soup = BeautifulSoup(page.content, "lxml")
            links = (GoogleScraper.get_url(x) for x in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")))
            for link in links:
                if not link.startswith(r'http://webcache.googleusercontent.com'):
                    yield link

    def __init__(self):
        self.url_base = "http://www.google.de/search?q="


class AmazonScraper(BaseScraper):
    def save(self, data, out_file):
        out_file.write(",".join(x for x in data) + '\n')

    def make_query(self, query):
        def init_driver():
            driver = webdriver.Firefox()
            driver.wait = WebDriverWait(driver, 5)
            return driver

        def lookup(driver, query):
            driver.get(self.url_base)
            try:
                box = driver.wait.until(EC.presence_of_element_located(
                    (By.NAME, "field-keywords")))
                button = driver.wait.until(EC.element_to_be_clickable(
                    (By.CLASS_NAME, "nav-input")))
                box.send_keys(query)
                button.click()
                time.sleep(5)
                return driver.current_url
            except TimeoutException:
                print("Box or Button not found in amazon")

        driver = init_driver()
        query_url = lookup(driver, query)
        time.sleep(5)
        driver.quit()
        return query_url

    def scrape(self, f):
        def extract_categories_refs(element):
            sp_list = ''.join(x.encode('utf-8') for x in element.find_all("span", {"class": "a-list-item"}))
            sp = BeautifulSoup(sp_list, "lxml", from_encoding='utf-8')

            li_list = ''.join(x.encode('utf-8') for x in sp.find_all("a", {"class": "a-link-normal s-ref-text-link"}))
            li = BeautifulSoup(li_list, "lxml", from_encoding='utf-8')

            href = li.find_all(href=True)  # ("span", {"class": "a-link-normal s-ref-text-link"})
            for h in href:
                if "a-size-small a-spacing-top-mini a-color-base a-text-bold" in h:
                    break
                try:
                    name = (BeautifulSoup(h.encode('utf-8'), "lxml", from_encoding='utf-8').find("span", {
                        "class": "a-size-small a-color-base"}).text)
                    name_href = (BeautifulSoup(h.encode('utf-8'), "lxml", from_encoding='utf-8').find("a", {
                        "class": "a-link-normal s-ref-text-link"})['href'])
                except Exception:
                    name = "none"
                    name_href = "none"
                if name is not "none":
                    yield (name, name_href)

        for query in tqdm(f):
            url = 'http' + self.make_query(query)[5:]
            headers = {
                'User-Agent': self.random_user_agent()}
            r = requests.get(url, headers=headers)
            r.encoding = 'utf-8'
            time.sleep(5)
            strainer = SoupStrainer('div', attrs={'id': 'leftNavContainer'})
            soup = BeautifulSoup(r.content, 'lxml', parse_only=strainer, from_encoding='utf-8')
            link = soup.find("div", {"aria-live": "polite"})
            for name, name_href in set(extract_categories_refs(link)):
                print u"name is {}".format(name)
                print u"ref is {}".format(name_href)
                yield (name, name_href)

    def __init__(self):
        super(AmazonScraper, self).__init__()
        self.url_base = "http://www.amazon.de"


def get_args():
    import argparse

    parser = argparse.ArgumentParser(description='google serp scraper')
    parser.add_argument('--noarg', action="store_true", default=False)
    parser.add_argument('--qfile', action="store", dest="qfile", default='qFile.txt')
    parser.add_argument('--sfile', action="store", dest="sfile", default='seFile.txt')
    parser.add_argument('--output', action="store", dest="output", default='out.txt')
    parser.add_argument('--filter', action="store", dest="filter")
    parser.add_argument('--addsonly', action="store", dest="addsonly")
    parser.add_argument('--engine', action="store", dest="engine")
    return parser.parse_args()


if __name__ == '__main__':
    parsed_args = get_args()
    if parsed_args.engine == "amazon":
        scraper = AmazonScraper()
    elif parsed_args.engine == "google":
        scraper = GoogleScraper()

    # check if the input file exists, if not exit
    if os.path.isfile(parsed_args.qfile):
        with codecs.open(parsed_args.qfile, "r", "utf-8") as qf:
            with codecs.open(parsed_args.output, "a", "utf-8") as of:
                for l in scraper.scrape(qf):
                    scraper.save(l, of)
    else:
        print("no query file provided")

    if parsed_args.filter:
        pass



        ######
        # TODO : add separate option to scrape ads only
        #####
