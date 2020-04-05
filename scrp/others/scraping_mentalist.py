import logging.config

logging.config.fileConfig('log/logging.conf')
from bs4 import BeautifulSoup
import re
import requests
import csv


class Scraping:
    first_page = 'https://ch.nicovideo.jp/mentalist/video'
    other_url_source = 'https://ch.nicovideo.jp/mentalist/video?&mode=&sort=f&order=d&type=&page='
    unnecessary_titles = [
        'このエントリーをはてなブックマークに追加',
        'この動画を登録している公開マイリスト一覧',
        'メンタリストDaiGoの「心理分析してみた！」'
    ]

    def __init__(self):
        self.logger = logging.getLogger()

    def how_many_pages_exists(self):
        html = requests.get(self.first_page)
        soup = BeautifulSoup(html.text, "html.parser")
        max_page_number = len(soup.find_all("option", value=True, text=re.compile('\d')))
        return max_page_number

    def pages(self, max_page_number):
        """ get all_related_url """
        all_pages = [self.first_page] + [self.other_url_source + str(i) for i in range(2, max_page_number)]
        return all_pages

    def search_tag(self, all_pages, writer):
        for page_url in all_pages:
            html = requests.get(page_url)
            soup = BeautifulSoup(html.text, "html.parser")
            key_tags = soup.find_all("a")
            self._get_titles(key_tags, writer)

    def _get_titles(self, tags, writer):
        for tag in tags:
            set_title = []
            title_name = tag.get("title")
            title_link = tag.get("href")
            if (title_name is None) or (title_name in self.unnecessary_titles):
                continue
            set_title.append([title_name, title_link])
            writer.writerows(set_title)


def main():
    sc = Scraping()
    f = open('mentalist_notes.csv', 'w')
    try:
        max_page_number = sc.how_many_pages_exists()
        pages = sc.pages(max_page_number)
        writer = csv.writer(f)
        sc.search_tag(pages, writer)
    except Exception as e:
        sc.logger.info(e)
    finally:
        f.close()


if __name__ == "__main__":
    main()
