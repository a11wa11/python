#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import re
import time

from bs4 import BeautifulSoup

from config_db.doda import Doda
from base_scraping import BaseScraping


class ScrapingDoda(BaseScraping):

    def __init__(self):
        super().__init__()
        self.table = Doda()
        # self.BASE_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList.action?ss=1&pic=1&ds=0&so=50&tp=1'
        self.BASE_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList.action?charset=SHIFT-JIS&fktt=4&kk=2&sid=TopSearch&usrclk=PC_logout_kyujinSearchArea_searchButton_job&oc=12L'

    def get_postal_code_and_address(self, parser: BeautifulSoup, match_address: object) -> tuple:
        postal_code, address = "", ""
        try:
            address_tag = parser.find("th", text=match_address)
            address_tag = parser.find("dt", text=match_address) if address_tag is None else address_tag
            if not address_tag:
                return
            address_tag_parent = address_tag.parent
            address = address_tag_parent.td
            address = address_tag_parent.dd if address is None else address
            address = super().replace_text(address.text)
            match_post = re.findall(self.match_post, address)
            if not match_post:
                return
            postal_code = match_post[0]
            address = re.sub(self.match_post, "", address).replace("〒", "")
        except Exception as e:
            self.logger.error("failed to get postal code and address.")
            self.logger.exception(e)
        finally:
            return postal_code, address

    def get_tel(self, url_doda_parser: BeautifulSoup, address: str) -> tuple:
        tel, remarks = "", ""
        try:
            tel_tag = url_doda_parser.find("dt", text=re.compile("連絡先"))
            if not tel_tag:
                return tel, remarks
            
            tel_tag_parent = tel_tag.parent.p
            if not self.match_tel.findall(tel_tag_parent.text):
                return tel, remarks
            
            tel = self.match_tel.findall(tel_tag_parent.text)
            tel = tel[0] if isinstance(tel, list) and tel != [] else tel
            remarks = tel_tag_parent.text.replace("\u3000", " ").replace(" ", "").replace(tel, "同TEL").replace(address, "同所在地")
            # 原因不明だがtelが定義できないときのため
            if not tel:
                tel = ""
        except Exception as e:
            self.logger.error("failed to get TEL and remarks.")
            self.logger.exception(e)
        finally:
            return tel, remarks

    def main(self):
        page_counter = 1
        data_counter = 1
        self.current_page_url = self.BASE_PAGE
        link_condition = "_JobListToDetail"
        max_page_parser = super().get_parser(self.current_page_url)
        match_address = re.compile("所在地")
        match_comp_url=re.compile("企業URL")
        company_terms = {'tag': 'p', 'class': 'job_title'}
        pagenation_terms = { 'tag': "a", 'class': "pagenation" }
        current_terms = { 'tag': "span", 'class': "current" }
        try:
            super().drop_table("doda")
            max_page_number = super().how_many_pages_exists(max_page_parser)
            while page_counter < max_page_number:
                self.logger.info(
                    ("starting analyze [%s/%s]: " % (str(page_counter), str(max_page_number))
                    ) + self.current_page_url
                )
                page_parser = super().get_parser(self.current_page_url)
                url_doda_list = super().get_companies_links_on_the_page(page_parser, link_condition)
                for url_doda in url_doda_list:
                    self.present_uri = url_doda
                    time.sleep(1)
                    try:
                        if '-tab__pr/' in url_doda:
                            url_doda = url_doda.replace('-tab__pr', '-tab__jd/-fm__jobdetail/-mpsc_sid__10')
                        url_doda_parser = super().get_parser(url_doda)
                        company_name = super().get_company_name(url_doda_parser, company_terms)
                        postal_code, address = self.get_postal_code_and_address(url_doda_parser, match_address)
                        tel, remarks = self.get_tel(url_doda_parser, address)
                        company_hp = super().get_commany_hp(url_doda_parser, match_comp_url)
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
                        self.logger.exception(e)
                        continue
                pagenations_parser = super().get_parser(self.current_page_url)
                next_page_url = super().get_next_page_url(pagenations_parser, pagenation_terms, current_terms)
                self.current_page_url = next_page_url
                page_counter += 1
            self.logger.info("finished analyze.")

        except Exception as e:
            self.logger.error("faild to fetching imformation at %s" % self.present_uri)
            self.logger.exception(e)


if __name__ == "__main__":
    ScrapingDoda().main()
