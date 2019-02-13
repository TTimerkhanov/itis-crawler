# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from __future__ import absolute_import
import scrapy


class PageItem(scrapy.Item):
    text = scrapy.Field()
    url = scrapy.Field()
