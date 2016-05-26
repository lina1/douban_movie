#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from scrapy.http import FormRequest, Request

from douban_moive.items import DoubanMoiveItem

from douban_moive.config.user_config import user_pass

__author__ = 'lina'
__date__ = '16/5/10'


class MovieSpider(CrawlSpider):
    name = "doubanmovie"
    allowed_domains = ["douban.com"]
    start_urls = ["https://movie.douban.com/top250"]

    # rules = [
    #     Rule(LinkExtractor(allow=r'https://movie.douban.com/top250\?start=\d+.*')),
    #     Rule(LinkExtractor(allow=r'https://movie.douban.com/subject/\d+',),
    #          callback="parse_item",
    #          # process_request="add_cookie"
    #     ),
    # ]

    # def add_cookie(self, request):
    #     request.replace(cookies=[
    #         {'name': 'dbcl2', 'value': '16536825:MaUDdd89GHQ', 'domain': '.douban.com', 'path': '/'},
    #     ])
    #     return request

    def start_requests(self):
        return [Request("https://accounts.douban.com/login", callback=self.post_login, meta={'cookiejar': 1})]
        # for i, url in enumerate(self.start_urls):
        #     yield FormRequest(url)

    def after_login(self, response):
        for i, url in enumerate(self.start_urls):
            yield FormRequest(url,
                              meta={'cookiejar': response.meta['cookiejar']},
                              callback=self.go_to_paginator
                              )

    def go_to_paginator(self, response):
        for href in response.css('.paginator a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield Request(full_url, meta={'cookiejar': response.meta['cookiejar']}, callback=self.go_to_film_page)

    def go_to_film_page(self, response):
        for url in response.css('.hd a::attr(href)'):
            # logging.log(url)
            yield Request(url.extract(), meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_item)

    def request_captcha(self, response):

        # get captcha url

        captcha = response.css('img[id="captcha_image"]::attr(src)').extract()
        if captcha:
            captcha_url = response.css('img[id="captcha_image"]::attr(src)').extract()[0]

            # download captcha
            yield Request(
                url=captcha_url,
                meta={
                    'cookiejar': response.meta['cookiejar'],
                },
                callback=self.download_captcha
            )

        else:
            self.post_login(response)

    def download_captcha(self, response):

        pass

    def post_login(self, response):

        return [FormRequest.from_response(response,
                                          # meta={'cookiejar': response.meta['cookiejar']},
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          formdata={
                                              'form_email': user_pass["email"],
                                              'form_password': user_pass["password"],
                                              'source': 'movie',
                                              'login': '登录',
                                              # 'redir': 'https://movie.douban.com/top250',
                                              'captcha-solution': ''
                                          },
                                          callback=self.after_login
                                          # dont_filter=True
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
