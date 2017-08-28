#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

browser = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': browser, }

url_base = "http://www.google.ca/search?q="


def make_query(url):
    return url_base + url


def get_url(link):
    raw = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0]
    return raw[:raw.rfind(r"&sa=U")]


def scrape(f):
    for url in tqdm(f):
        page = requests.get(make_query(url))
        soup = BeautifulSoup(page.content, "lxml")
        links = (get_url(x) for x in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")))
        for link in links:
            if not link.startswith(r'http://webcache.googleusercontent.com'):
                yield link


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Example with long option names',
    )
    parser.add_argument('--noarg', action="store_true",
                        default=False)

    parser.add_argument('--qfile', action="store",
                        dest="qfile", default='qFile.txt')
    parser.add_argument('--sfile', action="store",
                        dest="sfile", default='seFile.txt')
    parser.add_argument('--output', action="store",
                        dest="output", default='out.txt')
    parser.add_argument('--filter', action="store",
                        dest="filter", default='filter.txt')
    parsed_args = parser.parse_args()

    print(parsed_args.qfile)

    with open(parsed_args.qfile, "r") as qf:
        with open(parsed_args.output, "w") as of:
            for l in scrape(qf):
                of.write(l + '\n')
