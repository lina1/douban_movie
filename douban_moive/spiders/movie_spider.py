#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from scrapy.http import FormRequest

from douban_moive.items import DoubanMoiveItem

__author__ = 'lina'
__date__ = '16/5/10'


class MovieSpider(CrawlSpider):
    name = "doubanmovie"
    allowed_domains = ["movie.douban.com"]
    start_urls = ["https://movie.douban.com/top250"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.5.17 (KHTML, like Gecko) Version/9.1 Safari/601.5.17"
    }

    rules = [
        Rule(LinkExtractor(allow=r'https://movie.douban.com/top250\?start=\d+.*')),
        Rule(LinkExtractor(allow=r'https://movie.douban.com/subject/\d+'), callback="parse_item"),
    ]

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            yield FormRequest(url, headers=self.headers)

    def parse_item(self, response):
        sel = Selector(response)
        item = DoubanMoiveItem()
        item["name"] = sel.xpath('//*[@id="content"]/h1/span[1]/text()').extract()
        item["year"] = sel.xpath('//*[@id="content"]/h1/span[2]/text()').re(r'\((\d+)\)')
        item["score"] = sel.xpath('//*[@class="rating_num"]/text()').extract()
        item["director"] = sel.xpath('//*[@id="info"]/span[1]/a/text()').extract()
        item["classification"] = sel.xpath('//span[@property="v:genre"]/text()').extract()
        item["actor"] = sel.xpath('//*[@id="actor"]/a/text()').extract()





        # print item["name"]

        return item
