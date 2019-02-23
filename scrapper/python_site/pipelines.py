# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

from .spiders.python_site import PythonSiteSpider


class JsonWriterPipeline(object):
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(os.path.dirname(CURRENT_PATH), 'data')

    INDEX = {}
    COUNTER = 0

    def get_valid_path(self, path):
        valid_path = path.replace(PythonSiteSpider.start_urls[0], '')
        valid_path = valid_path.replace('.php', '.txt').replace('/', '_')
        return valid_path

    def generate_index_file(self):
        with open(f'{os.path.dirname(self.CURRENT_PATH)}/index.csv', 'w') as wr:
            wr.write('url,file\n')
            for url, file in self.INDEX.items():
                wr.write(f'{url},{file}\n')

    def close_spider(self, spider):
        self.generate_index_file()

    def process_item(self, item, spider):
        if item.get("url") not in self.INDEX.keys():
            path = f'{self.COUNTER}.txt'
            self.COUNTER += 1
            self.INDEX[item.get("url")] = path

            with open(f'{self.DATA_PATH}/{path}', 'w') as wr:
                wr.write(item.get('text'))
        return item
