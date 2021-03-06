#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import logging.config

import requests
from bs4 import BeautifulSoup

from config_db.database import db


class BaseScraping():

    def __init__(self):
        logging.config.fileConfig('config_python/logging.conf')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.table = None
        self.BASE_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList.action?ss=1&pic=1&ds=0&so=50&tp=1'
        self.OTHER_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList.action?pic=1&ds=0&so=50&tp=1&page='

    def drop_table(self, table_name: str):
        """ 既存のテーブルを削除する """
        try:
            if table_name in db.get_tables():
                db.drop_tables(self.table.__class__)
            db.create_tables([self.table.__class__])
        except Exception as e:
            self.logger.error("failed to drop %s table" % table_name)
            self.logger.exception(e)

    def get_parser(self, url: str) -> BeautifulSoup:
        """ 指定のURLからパーサーを取得する """
        html = requests.get(url)
        parser = BeautifulSoup(html.text, "html.parser")
        return parser

    def how_many_pages_exists(self, parser: BeautifulSoup) -> int:
        """ ページネーションから最大ページ数を取得する """
        max_page_number = int(parser.find_all("a", class_="pagenation")[-1].string)
        self.logger.info("Max Page is %s" % max_page_number)
        return max_page_number
    
    def get_per_page_urls(self, max_page_number: int) -> list:
        """ ページ数分の各URLを取得する """
        per_page_urls = [self.BASE_PAGE] + [self.OTHER_PAGE + str(i) for i in range(2, max_page_number + 1)]
        self.logger.info("got each pages URL.")
        return per_page_urls

    def get_next_page_url(self, pegenations_parser: BeautifulSoup) -> str:
        """ ページ数分の各URLを取得する """
        pagenations = pegenations_parser.find_all("a", class_="pagenation")
        current_page_num = int(pegenations_parser.find("span", class_="current").text)
        next_page_num = current_page_num + 1
        for pagenation in pagenations:
            if int(pagenation.text) == next_page_num:
                next_page_url = pagenation.get("href")
                return next_page_url
        self.logger.error("couldn't get next page url.")

    def search_recruit_info(self, per_page_urls: list) -> list:
        company_urls = []
        for page_url in per_page_urls:
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

    def get_company_name(self, parser: BeautifulSoup) -> str:
        return parser.find("p", "job_title").string

    def get_address(self, parser: BeautifulSoup) -> tuple:
        pass

    def get_tel(self, parser: object) -> tuple:
        pass

    def get_commany_hp(self, parser: BeautifulSoup, match_text=None) -> tuple:
        company_hp = ""
        hp_tag = parser.find(text=match_text)
        if hp_tag is not None:
            company_hp = hp_tag.parent.parent.a.text
            company_hp = company_hp.replace(" ", "").replace("\r\n", "").replace("\n", "")
        return company_hp

    def replace_text(self, raw_data: str, company=False, working_office=False) -> str:
        try:
            deleted_new_line_text = raw_data.replace("\r\n", "").replace("\n", "").replace("\r", "")
            deleted_spaces_text = re.sub("  +", "", deleted_new_line_text)
            text = deleted_spaces_text.replace("\u3000", " ").replace("\xa0", " ")
            if company is True:
                text = text.replace("株式会社 ", "(株)").replace("株式会社", "(株)")
            if working_office is True:
                text = text.replace("勤務地", "")
            return text
        except Exception as e:
            self.logger.error("failed to replace text.")
            self.logger.exception(e)
