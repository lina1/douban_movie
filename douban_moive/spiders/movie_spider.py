#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from scrapy.http import FormRequest, Request

from douban_moive.items import DoubanMoiveItem

from douban_moive.config import user_config

__author__ = 'lina'
__date__ = '16/5/10'


class MovieSpider(CrawlSpider):
    name = "doubanmovie"
    allowed_domains = ["douban.com"]
    start_urls = ["https://movie.douban.com/top250"]

    rules = [
        Rule(LinkExtractor(allow=r'https://movie.douban.com/top250\?start=\d+.*')),
        Rule(LinkExtractor(allow=r'https://movie.douban.com/subject/\d+'), callback="parse_item"),
    ]

    def start_requests(self):

        return [Request("https://accounts.douban.com/login", meta={"cookiejar": 1}, callback=self.request_captcha)]

    def after_login(self, response):
        for i, url in enumerate(self.start_urls):
            yield FormRequest(url)

    def request_captcha(self, response):

        # get captcha url
        captcha_url = response.css('img[id="captcha_image"]::attr(src)').extract()[0]

        # download captcha
        yield Request(
            url=captcha_url,
            meta={
                'cookiejar': response.meta['cookiejar'],
            },
            callback=self.download_captcha
        )

    def download_captcha(self, response):

        pass

    def post_login(self, response):

        return [FormRequest.from_response(response,
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          formdata={
                                              'form_email': user_config["email"],
                                              'form_password': user_config["password"],
                                              'source': 'movie',
                                              'login': '登录',
                                              'redir': 'https://movie.douban.com',
                                              'captcha-solution': ''
                                          },
                                          callback=self.after_login,
                                          dont_filter=True
                                          )]

    def parse_item(self, response):
        sel = Selector(response)
        item = DoubanMoiveItem()
        item["name"] = sel.xpath('//*[@id="content"]/h1/span[1]/text()').extract()
        item["year"] = sel.xpath('//*[@id="content"]/h1/span[2]/text()').re(r'\((\d+)\)')
        item["score"] = sel.xpath('//*[@property="v:average"]/text()').extract()
        item["director"] = sel.xpath('//*[@id="info"]/span[1]//a/text()').extract()
        item["classification"] = sel.xpath('//span[@property="v:genre"]/text()').extract()
        item["actor"] = sel.xpath('//*[@class="actor"]//a/text()').extract()

        return item
