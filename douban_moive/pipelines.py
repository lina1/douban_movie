# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
from scrapy import log

import MySQLdb


class DoubanMoivePipeline(object):

    def __init__(self):
        self.dbpool = adbapi.ConnectionPool(
            'MySQLdb',
            db='douban',
            user='root',
            passwd='root',
            cursorclass=MySQLdb.cursors.DictCursor,
            charset='utf8',
            use_unicode=False
        )

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
        return item

    def _conditional_insert(self, tx, item):
        tx.execute("select * from movie where m_name= %s", (item['name'][0],))
        result = tx.fetchone()
        if result:
            log.msg("Item already exists!")
        else:

            classification = actor = ''
            lenClassification = len(item['classification'])
            lenActor = len(item['actor'])
            for n in xrange(lenClassification):
                classification += item['classification'][n]
                if n < lenClassification - 1:
                    classification += '/'
            for n in xrange(lenActor):
                actor += item['actor'][n]
                if n < lenActor - 1:
                    actor += '/'

            tx.execute(\
                "insert into movie (m_name,m_year,m_score,m_director,m_classification,m_actor) values (%s,%s,%s,%s,%s,%s)", \
                (item['name'][0], item['year'][0], item['score'][0], item['director'][0], classification, actor))
            log.msg("Item stored in db: %s" % item, level=log.DEBUG)

    def handle_error(self, e):
        log.err(e)
