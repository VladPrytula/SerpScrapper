#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

browser = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': browser, }

url_base = "http://www.google.ca/search?q="


def make_query(query):
    return url_base + query.replace(" ", "+")


def get_url(link):
    raw = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0]
    return raw[:raw.rfind(r"&sa=U")]


def scrape_search_engine(f):
    for query in tqdm(f):
        print(query)
        print(make_query(query))
        page = requests.get(make_query(query))

        soup = BeautifulSoup(page.content, "lxml")
        links = (get_url(x) for x in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")))
        for link in links:
            if not link.startswith(r'http://webcache.googleusercontent.com'):
                yield link


def get_args():
    import argparse

    parser = argparse.ArgumentParser(description='google serp scraper')
    parser.add_argument('--noarg', action="store_true", default=False)
    parser.add_argument('--qfile', action="store", dest="qfile", default='qFile.txt')
    parser.add_argument('--sfile', action="store", dest="sfile", default='seFile.txt')
    parser.add_argument('--output', action="store", dest="output", default='out.txt')
    parser.add_argument('--filter', action="store", dest="filter", default='filter.txt')
    return parser.parse_args()


if __name__ == '__main__':
    parsed_args = get_args()

    # check if the input file exists, if not exit
    if os.path.isfile(parsed_args.qfile):
        with open(parsed_args.qfile, "r") as qf:
            with open(parsed_args.output, "w") as of:
                for l in scrape_search_engine(qf):
                    of.write(l + '\n')
    else:
        print("no query file provided")
