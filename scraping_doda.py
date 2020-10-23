#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import re
import time
import logging.config

import requests
from bs4 import BeautifulSoup

from config_db.database import db
from config_db.doda import Doda
from base_scraping import BaseScraping


class ScrapingDoda(BaseScraping):
    logging.config.fileConfig('config_python/logging.conf')

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.table = Doda
        self.BASE_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList/j_oc__0108M/-preBtn__3/'
        self.OTHER_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList.action?so=50&tp=1&preBtn=3&pic=0&oc=0108M&ds=0&page='

    def get_parser(self, url: str) -> BeautifulSoup:
        if '-tab__pr/' in url:
            url = url.replace('-tab__pr', '-tab__jd/-fm__jobdetail/-mpsc_sid__10')
        html = requests.get(url)
        parser = BeautifulSoup(html.text, "html.parser")
        return parser

    def search_recruit_info(self, per_page_urls: list) -> list:
        company_urls = []
        for page_url in per_page_urls:
            html = requests.get(page_url)
            parser = BeautifulSoup(html.text, "html.parser")
            key_tags = parser.find_all("a")
            company_url = self._company_info(key_tags)
            company_urls += company_url
        return company_urls

    def _company_info(self, key_tags: BeautifulSoup) -> list:
        set_company_link = []
        for key_tag in key_tags:
            if not "class" in key_tag.attrs or key_tag['class'] != ["_JobListToDetail"]:
                continue
            company_link = key_tag.get("href")
            if company_link not in set_company_link:
                set_company_link.append(company_link)
        return set_company_link

    def get_address(self, parser: BeautifulSoup, match_address: object) -> tuple:
        try:
            postal_code, address = "", ""
            address_tag = parser.find("th", text=match_address)
            address_tag = parser.find("dt", text=match_address) if address_tag is None else address_tag
            if not address_tag:
                return
            address_tag_parent = address_tag.parent
            address = address_tag_parent.td
            address = address_tag_parent.dd if address is None else address
            address = address.text.replace("\r\n", "").replace("\n", "").replace("　", " ")
            address = re.sub("  +", "", address)
            match_post = re.findall(r"[0-9]{3}-[0-9]{4}", address)
            if not match_post:
                return
            postal_code = match_post[0]
            address = re.sub(r"[0-9]{3}-[0-9]{4}", "", address).replace("〒", "")
        except Exception as e:
            self.logger.info(e)
        finally:
            return postal_code, address

    def get_tel(self, parser: object, match_tel: object, address: str) -> tuple:
        tel = ""
        remarks = ""
        tel_tag = parser.find("dt", text=re.compile("連絡先"))
        if not tel_tag:
            return tel, remarks
        
        tel_tag_parent = tel_tag.parent.p
        if not match_tel.findall(tel_tag_parent.text):
            return tel, remarks
        
        tel = match_tel.findall(tel_tag_parent.text)
        tel = tel[0] if isinstance(tel, list) and tel != [] else tel
        remarks = tel_tag_parent.text.replace("\u3000", " ").replace(" ", "").replace(tel, "同TEL").replace(address, "同所在地")
        # 原因不明だがtelが定義できないときのため
        if not tel:
            tel = ""
        return tel, remarks

    def main(self):
        if "doda" in db.get_tables():
            db.drop_tables(Doda)
        db.create_tables([Doda])

        match_address = re.compile("所在地")
        match_tel = re.compile(r'[\(]{0,1}[0-9]{2,4}[\)\-\(‐]{0,1}[0-9]{2,4}[\)\-－]{0,1}[0-9]{3,4}')

        try:
            max_page_number = super().how_many_pages_exists()
            per_page_urls = super().get_per_page_urls(max_page_number)
            company_urls = self.search_recruit_info(per_page_urls)
            for url in company_urls:
                time.sleep(1)
                try:
                    parser = self.get_parser(url)
                    company_name = super().get_company_name(parser)
                    postal_code, address = self.get_address(parser, match_address)
                    tel, remarks = self.get_tel(parser, match_tel, address)
                    company_hp = super().get_commany_hp(parser)
                    self.table.insert(
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
                    self.logger.error(e)
                    continue
        except Exception as e:
            self.logger.error(e)


if __name__ == "__main__":
    ScrapingDoda().main()
