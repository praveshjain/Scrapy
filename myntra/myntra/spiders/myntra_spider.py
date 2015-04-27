from scrapy import Spider
from scrapy.selector import Selector

from myntra.items import MyntraItem

class MyntraSpider(Spider):
    name = "myntra"
    allowed_domains = ["myntra.com"]
    start_urls = [
        "http://www.myntra.com/men-chinos-and-trousers?src=tn&nav_id=400"
    ]


    def parse(self, response):
        print(response)
        products = Selector(response).xpath('//ul[@class="results small"]/li')

        for product in products:
           print(product.extract())
           item = MyntraItem()
           item['title'] = product.xpath('.//div[@class="product"]/text()').extract()
           item['url'] = product.xpath('.//@href').extract()[0]
           yield item
           break
