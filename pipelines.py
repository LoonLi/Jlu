# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import redis

class JluPipeline(object):
    
    def __init__(self):
    	self.database = redis.Redis(host='127.0.0.1',port='8888',db=0)
    	self.count = 0

    def process_item(self, item, spider):
        self.database.hset(self.count,'url',item['url'])
        self.database.hset(self.count,'title',item['title'])
        self.database.hset(self.count,'html',item['html'])
        self.count=self.count+1

        return item
