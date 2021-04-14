import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FfirstcitizensttItem
from itemloaders.processors import TakeFirst
import datetime

pattern = r'(\xa0)?'

class FfirstcitizensttSpider(scrapy.Spider):
	now = datetime.datetime.now()
	year = now.year
	name = 'firstcitizenstt'
	start_urls = [f'https://www.firstcitizenstt.com/about/news-and-notices/press-releases-{year}.html']

	def parse(self, response):
		articles = response.xpath('//div[@class="circle"]')
		for article in articles:
			date = article.xpath('.//a/following-sibling::text()').get()
			date = re.findall(r'\w+\s\d+(?:st|nd|rd|th)?\s\d+', date)
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="circle"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))
		item = ItemLoader(item=FfirstcitizensttItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
