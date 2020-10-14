#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import re
import csv
import logging.config
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from config_db.database import db
from config_db.doda import Doda


class Scraping:
    BASE_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList/j_oc__0108M/-preBtn__3/'
    OTHER_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList.action?so=50&tp=1&preBtn=3&pic=0&oc=0108M&ds=0&page='
    logging.config.fileConfig('config_python/logging.conf')

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.table = Doda

    def how_many_pages_exists(self) -> int:
        html = requests.get(self.BASE_PAGE)
        parser = BeautifulSoup(html.text, "html.parser")
        max_page_number = int(parser.find_all("a", class_="pagenation")[-1].string)
        return max_page_number

    def all_pages(self, max_page_number: int) -> list:
        """ get all_related_url """
        all_pages = [self.BASE_PAGE] + [self.OTHER_PAGE + str(i) for i in range(2, max_page_number + 1)]
        return all_pages

    def search_recruit_info(self, all_pages: list) -> list:
        company_urls = []
        for page_url in all_pages:
            html = requests.get(page_url)
            parser = BeautifulSoup(html.text, "html.parser")
            key_tags = parser.find_all("a")
            company_url = self._company_info(key_tags)
            company_urls += company_url
        return company_urls

    @staticmethod
    def _company_info(key_tags) -> list:
        set_company_link = []
        for key_tag in key_tags:
            if "class" not in key_tag.attrs or key_tag['class'] != ["_JobListToDetail"]:
                continue
            company_link = key_tag.get("href")
            if company_link not in set_company_link:
                set_company_link.append(company_link)
        return set_company_link

    def get_parser(self, url: str) -> BeautifulSoup:
        if '-tab__pr/' in url:
            url = url.replace('-tab__pr', '-tab__jd/-fm__jobdetail/-mpsc_sid__10')
        html = requests.get(url)
        parser = BeautifulSoup(html.text, "html.parser")
        return parser

    def get_company_name(self, parser: BeautifulSoup) -> str:
            return parser.find("p", "job_title").string

    def get_address(self, parser: BeautifulSoup) -> tuple:
        try:
            address_match = re.compile("所在地")
            postal_code, address = "", ""
            address_tag = parser.find("th", text=address_match)
            if address_tag is None:
                address_tag = parser.find("dt", text=address_match)
            if address_tag:
                address_tag_parent = address_tag.parent
                address = address_tag_parent.td
                if address is None:
                    address = address_tag_parent.dd
                address = address.text.replace("\r\n", "").replace("\n", "").replace(" ", "").replace("　", "")
                post_match = re.findall(r"[0-9]{3}-[0-9]{4}", address)
                if post_match:
                    postal_code = post_match[0]
                    address = re.sub(r"[0-9]{3}-[0-9]{4}", "", address).replace("〒", "")
        except Exception as e:
            self.logger.info(e)
        finally:
            return postal_code, address

    def get_tel(self, parser: object) -> tuple:
        tel_match = re.compile(r'[\(]{0,1}[0-9]{2,4}[\)\-\(‐]{0,1}[0-9]{2,4}[\)\-－]{0,1}[0-9]{3,4}')
        tel = ""
        remarks = ""
        tel_tag = parser.find("dt", text=re.compile("連絡先"))
        if tel_tag:
            tel_tag_parent = tel_tag.parent.p
            if (tel_match.findall(tel_tag_parent.text) is not None) and (tel_match.findall(tel_tag_parent.text) != []):
                tel = tel_match.findall(tel_tag_parent.text)
                tel = tel[0] if isinstance(tel, list) and tel != [] else tel
                remarks = tel_tag_parent.text.replace("\u3000", " ").replace(" ", "")
                if not tel:
                    tel = ""
        return tel, remarks

    def get_commany_hp(self, parser: object) -> tuple:
        company_hp = ""
        hp_tag = parser.find(text=re.compile("企業URL"))
        if hp_tag is not None:
            company_hp = hp_tag.parent.parent.a.text
            company_hp = company_hp.replace(" ", "").replace("\r\n", "").replace("\n", "")
        return company_hp

    def main(self):
        if not db.table_exists(Doda):
            db.create_tables([Doda])
        try:
            max_page_number = self.how_many_pages_exists()
            all_pages = self.all_pages(max_page_number)
            company_urls = self.search_recruit_info(all_pages)
            for url in company_urls:
                try:
                    parser = self.get_parser(url)
                    company_name = self.get_company_name(parser)
                    postal_code, address = self.get_address(parser)
                    tel, remarks = self.get_tel(parser)
                    company_hp = self.get_commany_hp(parser)
                    Doda.insert(
                        company_name = company_name,
                        url_doda = url,
                        postal_code = postal_code,
                        address = address,
                        TEL = tel,
                        remarks = remarks,
                        url_company = company_hp
                    ).execute()
                    self.logger.info(company_name + " was sucessfully inserted")
                except Exception as e:
                    self.logger.info(e)
                    continue
        except Exception as e:
            self.logger.error(e)


if __name__ == "__main__":
    Scraping().main()
