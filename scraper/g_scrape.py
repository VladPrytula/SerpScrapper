#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
from tqdm import tqdm


def get_url(link):
    raw = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0]
    return raw[:raw.rfind(r"&sa=U")]


class Scraper():
    def __init__(self, engine_base):
        self.browser = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'  # 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers = {'User-Agent': self.browser, }
        self.url_base = engine_base  # "http://www.google.de/search?q="

    def make_query(self, query):
        return self.url_base + query.replace(" ", "+")

    def scrape_search_engine(self, f):
        for query in tqdm(f):
            page = requests.get(self.make_query(query))
            soup = BeautifulSoup(page.content, "lxml")
            links = (get_url(x) for x in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")))
            for link in links:
                if not link.startswith(r'http://webcache.googleusercontent.com'):
                    yield link

    def amazon_scrape_search_engine(self):

        def extract_categories_refs(element):
            sp_list = ''.join(x.encode('utf-8') for x in element.find_all("span", {"class": "a-list-item"}))

            sp = BeautifulSoup(sp_list, "lxml", from_encoding='utf-8')

            li_list = ''.join(x.encode('utf-8') for x in sp.find_all("a", {"class": "a-link-normal s-ref-text-link"}))
            li = BeautifulSoup(li_list, "lxml", from_encoding='utf-8')
            href = li.find_all(href=True)  # ("span", {"class": "a-link-normal s-ref-text-link"})
            for h in href:
                if "a-size-small a-spacing-top-mini a-color-base a-text-bold" in h:
                    break
                print (BeautifulSoup(h.encode('utf-8'), "lxml", from_encoding='utf-8').find("span", {
                    "class": "a-size-small a-color-base"}).text)
                print (BeautifulSoup(h.encode('utf-8'), "lxml", from_encoding='utf-8').find("a", {
                    "class": "a-link-normal s-ref-text-link"})['href'])

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}  # {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(
            'https://www.amazon.de/s/ref=nb_sb_noss_2?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&url=search-alias%3Daps&field-keywords=macbook&rh=i%3Aaps%2Ck%3Amacbook',
            headers=headers)
        r.encoding = 'utf-8'
        time.sleep(5)
        strainer = SoupStrainer('div', attrs={'id': 'leftNavContainer'})
        soup = BeautifulSoup(r.content, 'lxml', parse_only=strainer, from_encoding='utf-8')
        link = soup.find("div", {"aria-live": "polite"})
        extract_categories_refs(link)


def get_args():
    import argparse

    parser = argparse.ArgumentParser(description='google serp scraper')
    parser.add_argument('--noarg', action="store_true", default=False)
    parser.add_argument('--qfile', action="store", dest="qfile", default='qFile.txt')
    parser.add_argument('--sfile', action="store", dest="sfile", default='seFile.txt')
    parser.add_argument('--output', action="store", dest="output", default='out.txt')
    parser.add_argument('--filter', action="store", dest="filter")
    parser.add_argument('--addsonly', action="store", dest="addsonly")
    return parser.parse_args()


if __name__ == '__main__':
    parsed_args = get_args()

    g_scraper = Scraper("http://www.google.de/search?q=")
    a_scraper = Scraper(
        "https://www.amazon.de")  # /s/ref=nb_sb_noss_1?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&url=search-alias=aps&field-keywords=")

    a_scraper.amazon_scrape_search_engine()


    # check if the input file exists, if not exit
    # if os.path.isfile(parsed_args.qfile):
    #     with open(parsed_args.qfile, "r") amazon_selenium.py qf:
    #         with open(parsed_args.output, "a") amazon_selenium.py of:
    #             for l in g_scraper.scrape_search_engine(qf):
    #                 of.write(l + '\n')
    # else:
    #     print("no query file provided")
    #
    # if parsed_args.filter:
    #     pass



    ######
    # TODO : add separate option to scrape ads only
    #####
