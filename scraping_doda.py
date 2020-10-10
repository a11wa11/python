#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from datetime import datetime
import csv
import logging.config

logging.config.fileConfig('config_python/logging.conf')
from bs4 import BeautifulSoup
import re
import requests


class Scraping:
    BASE_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList/j_oc__0108M/-preBtn__3/'
    OTHER_PAGE = 'https://doda.jp/DodaFront/View/JobSearchList.action?so=50&tp=1&preBtn=3&pic=0&oc=0108M&ds=0&page='

    def __init__(self):
        self.logger = logging.getLogger()

    def how_many_pages_exists(self):
        html = requests.get(self.BASE_PAGE)
        soup = BeautifulSoup(html.text, "html.parser")
        max_page_number = int(soup.find_all("a", class_="pagenation")[-1].string)
        return max_page_number

    def all_pages(self, max_page_number):
        """ get all_related_url """
        all_pages = [self.BASE_PAGE] + [self.OTHER_PAGE + str(i) for i in range(2, max_page_number + 1)]
        return all_pages

    def search_recruit_info(self, all_pages):
        company_urls = []
        for page_url in all_pages:
            html = requests.get(page_url)
            soup = BeautifulSoup(html.text, "html.parser")
            key_tags = soup.find_all("a")
            company_url = self._company_info(key_tags)
            company_urls += company_url
        return company_urls

    @staticmethod
    def _company_info(key_tags):
        set_company_link = []
        for key_tag in key_tags:
            if "class" not in key_tag.attrs or key_tag['class'] != ["_JobListToDetail"]:
                continue
            company_link = key_tag.get("href")
            if company_link not in set_company_link:
                set_company_link.append(company_link)
        return set_company_link

    def company_details(self, company_urls, writer):
        for url in company_urls:
            if '-tab__pr/' in url:
                url = url.replace('-tab__pr', '-tab__jd/-fm__jobdetail/-mpsc_sid__10')
            html = requests.get(url)
            soup = BeautifulSoup(html.text, "html.parser")
            company_name = soup.find("p", "job_title").string
            set_record = [[company_name, url]]
            try:
                set_record = self.get_address(set_record, soup)
                set_record = self.get_tel(set_record, soup)
            except Exception as e:
                self.logger.info(e)
                continue
            finally:
                writer.writerows(set_record)

    def get_address(self, set_record: object, soup: object) -> object:
        try:
            address_match = re.compile("所在地")
            post_number, address = "-", "_"
            address_tag = soup.find("th", text=address_match)
            if address_tag is None:
                address_tag = soup.find("dt", text=address_match)
            if address_tag:
                address_tag_parent = address_tag.parent
                address = address_tag_parent.td
                if address is None:
                    address = address_tag_parent.dd
                address = address.text.replace("\r\n", "").replace("\n", "").replace(" ", "").replace("　", "")
                post_match = re.findall(r"〒[0-9]{3}-[0-9]{4}", address)
                if post_match:
                    post_number = post_match[0]
                    address = re.sub(r"〒[0-9]{3}-[0-9]{4}", "", address)
        except Exception as e:
            self.logger.info(e)
        finally:
            set_record[0] += [post_number, address]
            return set_record

    def get_tel(self, set_record, soup):
        try:
            tel_match = re.compile(r'[\(]{0,1}[0-9]{2,4}[\)\-\(‐]{0,1}[0-9]{2,4}[\)\-－]{0,1}[0-9]{3,4}')
            tel = "-"
            remarks = "-"
            company_hp = "-"
            tel_tag = soup.find("dt", text=re.compile("連絡先"))
            if tel_tag:
                tel_tag_parent = tel_tag.parent.p
                if (tel_match.findall(tel_tag_parent.text) is not None) and (tel_match.findall(tel_tag_parent.text) != []):
                    tel = tel_match.findall(tel_tag_parent.text)
                    tel = tel[0] if isinstance(tel, list) and tel != [] else tel
                    remarks = tel_tag_parent.text.replace("\u3000", " ").replace(" ", "")
                    if not tel:
                        tel = "-"

            hp_tag = soup.find(text=re.compile("企業URL"))
            if hp_tag is not None:
                company_hp = hp_tag.parent.parent.a.text
                company_hp = company_hp.replace(" ", "")
        except Exception as e:
            self.logger.info(e)
        finally:
            set_record[0].append("TEL: " + tel)
            set_record[0].append(remarks)
            set_record[0].append(company_hp)
            return set_record


def main():
    sc = Scraping()
    file_name = './outputs/doda_scrp_%s.scv' % datetime.today().strftime("%Y%m%d_%H%M")
    f = open(file_name, 'w')
    try:
        writer = csv.writer(f)
        writer.writerows([["会社名", "URL", "郵便番号", "住所", "TEL", "備考"]])
        max_page_number = sc.how_many_pages_exists()
        all_pages = sc.all_pages(max_page_number)
        company_urls = sc.search_recruit_info(all_pages)
        sc.company_details(company_urls, writer)
    except Exception as e:
        sc.logger.info(e)
    finally:
        f.close()


if __name__ == "__main__":
    main()
