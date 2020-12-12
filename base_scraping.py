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
        self.current_page_url = None
        self.match_tel = re.compile(r'[\(]{0,1}[0-9]{2,4}[\)\-\(‐]{0,1}[0-9]{2,4}[\)\-－]{0,1}[0-9]{3,4}')
        self.match_post = re.compile(r'[0-9]{3}-[0-9]{4}')
        self.present_uri = None

    def drop_table(self, table_name: str):
        """ 既存のテーブルを削除する """
        try:
            if table_name in db.get_tables():
                db.drop_tables(self.table.__class__)
            db.create_tables([self.table.__class__])
            self.logger.info("recreated %s_table." % table_name)
        except Exception as e:
            self.logger.error("failed to drop %s table" % table_name)
            self.logger.exception(e)

    def get_parser(self, url: str) -> BeautifulSoup:
        """ 指定のURLからパーサーを取得する """
        html = requests.get(url)
        parser = BeautifulSoup(html.text, "html.parser")
        return parser

    def how_many_job_offers_exists(self, parser: BeautifulSoup) -> int:
        """ 求人数を取得する """
        try:
            max_job_offers = int(parser.find_all("span", class_="js-resultCount")[-1].string)
            self.logger.info("Max Number of Job-offers is %s" % max_job_offers)
            return max_job_offers
        except Exception as e:
            self.logger.error("failed to get number of max job offers")
            self.logger.exception(e)

    def how_many_pages_exists(self, parser: BeautifulSoup) -> int:
        """ ページネーションから最大ページ数を取得する """
        max_page_number = int(parser.find_all("a", class_="pagenation")[-1].string)
        self.logger.info("Max Page is %s" % max_page_number)
        return max_page_number
    
    def get_companies_links_on_the_page(self, page_parser: BeautifulSoup, link_condition: str) -> list:
        """ 各企業の求人詳細ページリンクを取得する """
        try:
            links = page_parser.find_all("a")
            companies_links_list = []
            for link in links:
                if "class" not in link.attrs or link_condition not in link['class']:
                    continue
                company_link = link.get("href")
                if company_link not in companies_links_list:
                    companies_links_list.append(company_link)
            return companies_links_list
        except Exception as e:
            self.logger.error("failed to get companies_links on the page:%s" % self.current_page_url)
            self.logger.exception(e)

    def get_next_page_url(self, pagenations_parser: BeautifulSoup, pagenation_terms: dict, current_terms: dict) -> str:
        """ ページ数分の各URLを取得する """
        try:
            pagenations = pagenations_parser.find_all(pagenation_terms['tag'], class_=pagenation_terms['class'])
            current_page_num = int(pagenations_parser.find(current_terms['tag'], class_=current_terms['class']).text)
            next_page_num = current_page_num + 1
            for pagenation in pagenations:
                if int(pagenation.text) == next_page_num:
                    next_page_url = pagenation.get("href")
                    return next_page_url
        except Exception as e:
            self.logger.error("couldn't get next page url.")
            self.logger.exception(e)

    def get_company_name(self, parser: BeautifulSoup, company_terms: dict) -> str:
        """ 会社名を取得する """
        try:
            company_name_raw_data = parser.find(company_terms['tag'], company_terms['class']).string
            company_name = self.replace_text(company_name_raw_data, company=True)
            return company_name
        except Exception as e:
            self.logger.error("failed to get company_name.")
            self.logger.exception(e)

    def get_address(self, parser: BeautifulSoup) -> tuple:
        pass

    def get_tel(self, parser: object) -> tuple:
        pass

    def get_commany_hp(self, parser: BeautifulSoup, match_text=None) -> tuple:
        """ 企業ホームページを取得する """
        try:
            company_hp = ""
            hp_tag = parser.find(text=match_text)
            if hp_tag is not None:
                company_hp_raw_data = hp_tag.parent.parent.a.text
                company_hp = self.replace_text(company_hp_raw_data)
            return company_hp
        except Exception as e:
            self.logger.error("failed to get the commany's website URI.")
            self.logger.exception(e)

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
