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

    def get_valid_path(self, path):
        path = path.replace(PythonSiteSpider.start_urls[0], '')
        path = path.replace('.php', '.txt')
        return path.replace('/', '_')

    # def open_spider(self, spider):
    #     self.file = open('items.json', 'w', encoding='utf-8')
    #
    # def close_spider(self, spider):
    #     self.file.close()

    # def process_item(self, item, spider):
    #     line = json.dumps(dict(item), ensure_ascii=False) + "\n"
    #     self.file.write(line)
    #     return item

    def process_item(self, item, spider):
        path = self.get_valid_path(item.get("url"))
        with open(f'{self.DATA_PATH}/{path}', 'w') as wr:
            wr.write(item.get('text'))
        return item
