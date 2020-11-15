#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import re
import time
import logging.config

from bs4 import BeautifulSoup

from config_db.database import db
from config_db.doda import Doda
from base_scraping import BaseScraping


class ScrapingDoda(BaseScraping):

    def __init__(self):
        logging.config.fileConfig('config_python/logging.conf')
        self.logger = logging.getLogger(__name__)
        self.table = Doda()
        # self.BASE_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList.action?ss=1&pic=1&ds=0&so=50&tp=1'
        self.BASE_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList.action?charset=SHIFT-JIS&fktt=4&kk=2&sid=TopSearch&usrclk=PC_logout_kyujinSearchArea_searchButton_job&oc=12L'

    def get_company_urls_on_the_page(self, page_parser: BeautifulSoup) -> list:
        key_tags = page_parser.find_all("a")
        company_urls = []
        for key_tag in key_tags:
            if not "class" in key_tag.attrs or key_tag['class'] != ["_JobListToDetail"]:
                continue
            company_link = key_tag.get("href")
            if company_link not in company_urls:
                company_urls.append(company_link)
        return company_urls

    def get_postal_code_and_address(self, parser: BeautifulSoup, match_address: object) -> tuple:
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

    def get_tel(self, url_doda_parser: BeautifulSoup, match_tel: object, address: str) -> tuple:
        tel, remarks = "", ""
        tel_tag = url_doda_parser.find("dt", text=re.compile("連絡先"))
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
        current_page_url = self.BASE_PAGE
        page_counter = 1
        data_counter = 1
        parser = super().get_parser(current_page_url)

        try:
            max_page_number = super().how_many_pages_exists(parser)
            while page_counter < max_page_number:
                self.logger.info(
                    ("starting analyze [%s/%s]: " % (str(page_counter), str(max_page_number))
                    ) + current_page_url
                )
                page_parser = super().get_parser(current_page_url)
                company_urls = self.get_company_urls_on_the_page(page_parser)
                for url_doda in company_urls:
                    time.sleep(1)
                    try:
                        if '-tab__pr/' in url_doda:
                            url_doda = url_doda.replace('-tab__pr', '-tab__jd/-fm__jobdetail/-mpsc_sid__10')
                        url_doda_parser = super().get_parser(url_doda)
                        company_name = super().get_company_name(url_doda_parser)
                        postal_code, address = self.get_postal_code_and_address(url_doda_parser, match_address)
                        tel, remarks = self.get_tel(url_doda_parser, match_tel, address)
                        company_hp = super().get_commany_hp(url_doda_parser)
                        self.table.insert(
                            company_name = company_name,
                            url_doda = url_doda,
                            postal_code = postal_code,
                            address = address,
                            TEL = tel,
                            remarks = remarks,
                            url_company = company_hp
                        ).execute()
                        self.logger.info(str(data_counter) + ": " + company_name + " was sucessfully inserted")
                        data_counter += 1
                    except Exception as e:
                        self.logger.error(e)
                        continue
                pegenations_parser = super().get_parser(current_page_url)
                next_page_url = super().get_next_page_url(pegenations_parser)
                current_page_url = next_page_url
                page_counter += 1
            self.logger.info("finished analyze.")

        except Exception as e:
            self.logger.error(e)


if __name__ == "__main__":
    ScrapingDoda().main()
