#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import re
import time
import logging.config

import requests
from bs4 import BeautifulSoup

from config_db.database import db
from config_db.rikunabi import Rikunabi
from base_scraping import BaseScraping


class ScrapingRikunabi(BaseScraping):

    def __init__(self):
        logging.config.fileConfig('config_python/logging.conf')
        self.logger = logging.getLogger(__name__)
        self.table = Rikunabi()
        self.BASE_PAGE = 'https://next.rikunabi.com/lst_new/?leadtc=top_new_lst'
        self.rikunabi_uri = 'https://next.rikunabi.com'
        self.present_uri = None
        self.match_tel = re.compile(r'[\(]{0,1}[0-9]{2,4}[\)\-\(‐]{0,1}[0-9]{2,4}[\)\-－]{0,1}[0-9]{3,4}')
        self.recruit_agent = False

    def how_many_job_offers_exists(self, parser: BeautifulSoup) -> int:
        """ 求人数を取得する """
        try:
            max_job_offers = int(parser.find_all("span", class_="js-resultCount")[-1].string)
            self.logger.info("Max Number of Job-offers is %s" % max_job_offers)
            return max_job_offers
        except Exception as e:
            self.logger.error("failed to get number of max job offers")
            self.logger.error(e)

    def get_companies_links_on_the_page(self, parser: BeautifulSoup) -> list:
        """ 各企業の求人詳細ページリンクを取得する """
        try:
            links = parser.find_all("a")
            companies_links_list = []
            for link in links:
                if ("class" not in link.attrs) or ("rnn-linkText" and "rnn-linkText--black" not in link['class']):
                    continue
                company_link = self.rikunabi_uri + link.get("href")
                if company_link not in companies_links_list:
                    companies_links_list.append(company_link)
            return companies_links_list
        except Exception as e:
            self.logger.error("failed to get companies_links on the page:%s" % self.current_page_url)
            self.logger.error(e)

    def replace_n5_url(self, parser: BeautifulSoup) -> str:
        try:
            link_tag = parser.find_all("a", class_='rn3-companyOfferTabMenu__navItemLink js-tabRecruitment')[0]
            replaced_company_link = self.rikunabi_uri + link_tag.get("href")
            return replaced_company_link
        except Exception as e:
            self.logger.error("failed to replace url.")
            self.logger.error(e)

    def fetch_parser(self, url: str) -> BeautifulSoup:
        """ 求人詳細の解析を取得する """
        html = requests.get(url)
        if "Windows" in html.encoding:
            html.encoding = html.apparent_encoding
        parser = BeautifulSoup(html.text, "html.parser")
        return parser

    def check_recruit_agent(self, parser: BeautifulSoup):
        """ エージェント案件か確認 """
        if len(parser.find_all("div", class_="rn3-agentServiceBK__title")) > 0:
            self.recruit_agent = True
        else:
            self.recruit_agent = False

    def get_company_name(self, parser: BeautifulSoup) -> str:
        """ 会社名を取得する """
        try:
            if self.recruit_agent == True:
                company_name_txt = parser.find("p", class_="rnn-offerCompanyName").string
            else:
                company_name_txt = parser.find("a", class_="rn3-companyOfferCompany__link js-companyOfferCompany__link").string
            company_name = super().replace_text(company_name_txt, True)
            return company_name
        except Exception as e:
            self.logger.error("failed to get company_name.")
            self.logger.error(e)

    def get_address(self, parser: BeautifulSoup) -> str:
        """ 連絡先住所を取得する """
        address = None
        try:
            if self.recruit_agent == True:
                raw_data_address = parser.find("th", class_="rnn-col-2", text="事業所").parent.p
            else:
                address_lists = parser.find_all("h3", class_="rn3-companyOfferEntry__heading", text="連絡先")
                if len(address_lists) > 1:
                    self.logger.info("2 more contacts in the page. review the program.")
                    return
                elif len(address_lists) < 1:
                    return
                raw_data_address = address_lists[0].find_next_siblings()[0]

            address = raw_data_address.text
            address = re.sub(r"〒[0-9]{3}-[0-9]{4}", "", address)
            address = super().replace_text(address)
        except Exception as e:
            self.logger.error("failed to get address.")
            self.logger.error(e)
        finally:
            return address 

    def get_postal_code(self, parser: BeautifulSoup) -> str:
        """ 郵便番号を取得する """
        postal_code = None
        try:
            if self.recruit_agent == True:
                raw_data_address = parser.find("th", class_="rnn-col-2", text="事業所").parent.p
            else:
                address_lists = parser.find_all("h3", class_="rn3-companyOfferEntry__heading", text="連絡先")
                if len(address_lists) > 1:
                    self.logger.info("2 more contacts in the page. review the program.")
                    return
                elif len(address_lists) < 1:
                    return
                raw_data_address = address_lists[0].find_next_siblings()[0]
            match_address = re.findall(r"〒[0-9]{3}-[0-9]{4}.+", raw_data_address.text)
            if not match_address:
                return
            postal_code = re.findall(r"〒[0-9]{3}-[0-9]{4}", match_address[0])
            postal_code = postal_code[0].replace("〒", "")
        except Exception as e:
            self.logger.error("failed to get postal code.")
            self.logger.error(e)
        finally:
            return postal_code

    def get_tel(self, parser: BeautifulSoup) -> str:
        """ 電話番号を取得する """
        tel = None
        try:
            if self.recruit_agent == True:
                return
            tel_candidates = parser.find_all("h3", class_="rn3-companyOfferEntry__heading")
            tel_candidate = [candidate for candidate in tel_candidates if "連絡先" in candidate.text][0]
            if not tel_candidate:
                return
            tel_tag = tel_candidate.find_next_siblings()[0]
            tel_elem = self.match_tel.findall(tel_tag.text)
            if not tel_elem:
                return
            tel = tel_elem[0]
        except Exception as e:
            self.logger.error("failed to get tel.")
            self.logger.error(e)
        finally:
            return tel
        
    def get_working_offices(self, parser: BeautifulSoup) -> str:
        """ 勤務地を取得する """
        working_offices = None
        try:
            if self.recruit_agent == True:
                element = parser.find("th", class_="rnn-col-2", text="勤務地").parent
            else:
                working_offices_candidates = parser.find_all("h3", class_="rn3-companyOfferRecruitment__heading")
                working_offices_candidate = [candidate for candidate in working_offices_candidates if "勤務地" in candidate.text][0]
                if not working_offices_candidate:
                    return
                element = working_offices_candidate.find_next_siblings()[0]
            working_offices = super().replace_text(element.text, working_office=True)
        except Exception as e:
            self.logger.error("failed to get working office.")
            self.logger.error(e)
        finally:
            return working_offices

    def get_commany_hp(self, parser: BeautifulSoup) -> str:
        """ 企業ホームページを取得する """
        try:
            company_hp = None
            if not parser.find("a", text="ホームページ"):
                return company_hp
            hp_tag = parser.find("a", text="ホームページ").get("href")
            if hp_tag is not None:
                company_hp = self.rikunabi_uri + hp_tag
            return company_hp
        except Exception as e:
            self.logger.error("failed to get the commany's website URI.")
            self.logger.error(e)

    def get_next_page_url(self, pegenations_parser: BeautifulSoup) -> str:
        """ ページ数分の各URLを取得する """
        try:
            pagenations = pegenations_parser.find_all("li", class_="rnn-pagination__page")
            current_page_num = int(pegenations_parser.find("li", class_="is-current").text)
            next_page_num = current_page_num + 1
            for pagenation in pagenations:
                if int(pagenation.text) == next_page_num:
                    next_page_url = self.rikunabi_uri + pagenation.findChild().get("href")
                    return next_page_url
        except Exception as e:
            self.logger.error("failed to get next page url.")
            self.logger.error(e)

    def main(self):
        page_counter = 1
        data_counter = 1
        self.current_page_url = self.BASE_PAGE
        job_offers_parser = super().get_parser(self.current_page_url)

        try:
            super().drop_table("rikunabi")
            max_job_offers = self.how_many_job_offers_exists(job_offers_parser)
            while data_counter < max_job_offers:
                self.logger.info(
                    ("starting analyze [%s/%s]: " % (str(data_counter), str(max_job_offers))
                    ) + self.current_page_url
                )
                page_parser = super().get_parser(self.current_page_url)
                url_rikunabi_list = self.get_companies_links_on_the_page(page_parser)
                for url_rikunabi in url_rikunabi_list:
                    self.present_uri = url_rikunabi
                    time.sleep(1)
                    try:
                        if 'n5_ttl' in url_rikunabi:
                            prepare_parser = super().get_parser(url_rikunabi)
                            url_rikunabi = self.replace_n5_url(prepare_parser)
                        url_rikunabi_parser = self.fetch_parser(url_rikunabi)
                        self.check_recruit_agent(url_rikunabi_parser)

                        company_name = self.get_company_name(url_rikunabi_parser)
                        address = self.get_address(url_rikunabi_parser)
                        postal_code = self.get_postal_code(url_rikunabi_parser)
                        tel = self.get_tel(url_rikunabi_parser)
                        working_office = self.get_working_offices(url_rikunabi_parser)
                        company_hp = self.get_commany_hp(url_rikunabi_parser)
                        
                        self.table.insert(
                            company_name = company_name,
                            url_rikunabi = url_rikunabi,
                            postal_code = postal_code,
                            address = address,
                            TEL = tel,
                            remarks = working_office,
                            url_company = company_hp
                        ).execute()
                        self.logger.info(str(data_counter) + ": " + company_name + " was sucessfully inserted")
                        data_counter += 1
                    except Exception as e:
                        self.logger.error(e)
                        continue
                pegenations_parser = super().get_parser(self.current_page_url)
                next_page_url = self.get_next_page_url(pegenations_parser)
                self.current_page_url = next_page_url
                page_counter += 1
            self.logger.info("finished analyze.")

        except Exception as e:
            self.logger.error("faild to fetching imformation at %s" % self.present_uri)
            self.logger.error(e)


if __name__ == "__main__":
    ScrapingRikunabi().main()
