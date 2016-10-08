import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class JluSpider(CrawlSpider):
	name = "Jlu"
	#allow_domains = ["jlu.edu.cn"]
	start_urls = ["http://zsb.jlu.edu.cn/list/45.html"]
	
	rules = (
	
		Rule(LinkExtractor(allow=('jlu.edu.cn', ),unique=True,deny=('xuebao.jlu.edu.cn','sjdz.jlu.edu.cn','http://bbs.jlu.edu.cn/',)), callback='parse_item',follow=True),
	
	)
	
	def parse_item(self,response):
		item = scrapy.Field()
		item['title'] = response.xpath('//title/text()').extract()
		item['url'] = response.url
		item['html'] = response.body
		return item