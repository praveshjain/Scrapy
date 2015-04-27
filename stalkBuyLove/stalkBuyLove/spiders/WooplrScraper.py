from scrapy import Spider, Item, Field, Selector
from pymongo import MongoClient
import time,os
from scrapy.http import Request

class WooplrSpider(Spider):

    name, start_urls = 'stalkBuyLove', ['http://www.stalkbuylove.com/new-arrivals/week-2.html']
    product_list=[]
    count=1

    def parse(self, response):
        self.count=self.count+1
        print "Parsing webpage..."
        additional_info = response.xpath("//div[@class='additional_info']")
        product_detail = response.xpath("//div[@class='product-detail-slide']")
        for info,detail in zip(additional_info,product_detail):

            product = {}
            name = detail.css('a::attr(title)').extract()[0]

            availability = {"3XS":"NA", "2XS":"NA", "XS":"NA", "S":"NA", "M":"NA", "L":"NA", "XL":"NA", "2XL":"NA", "3XL":"NA"}
            
            sizes = info.re(r'/SBL/(.*?)\.png')

            for size in sizes:
                availability[size]="A"

            reg_price = detail.xpath(".//span[@class='regular-price']")
            org_price = detail.xpath(".//span[@class='price org_price']")
            special_price = detail.xpath(".//span[@class='price special_label']")
            if reg_price != []:
                price = reg_price.re(r'Rs\. ([0-9,]+)')[0].replace(',' , '')
                discounted_price = price
            else:
                price = org_price.re(r'Rs\. ([0-9,]+)')[0].replace(',' , '')
                discounted_price = special_price.re(r'Rs\. ([0-9,]+)')[0].replace(',' , '')

            product = {"Name" : name, "Price" : price, "Discounted Price" : discounted_price, "Availability": availability}

            WooplrSpider.product_list.append(product)
        req = Request(url='http://www.stalkbuylove.com/new-arrivals/week-2.html?p='+str(self.count))
        next_page = response.xpath("//a[@class='next i-next']").extract()
        if next_page==[]:
            req=None
            self.store_and_compare()
        return req
            


    def store_and_compare(self):
        print "Storing and Comparing..."
        client = MongoClient()
        db = client.SBL_db
        collection = db.products_coll
        posts=db.posts
        old_db = posts.find()
        log = time.strftime("%x") + " " + time.strftime("%X") + " Ran CRON job\n"
        for entry in old_db:
            for product in self.product_list:
                if product["Name"] == entry["Name"]:
                    old_avail = entry["Availability"]
                    new_avail = product["Availability"]
                    for key in old_avail.keys():
                        if old_avail[key]!=new_avail[key]:
                            log = log + time.strftime("%x") + " " + time.strftime("%X") + " Availability of " + product["Name"] + " changed for size " + key + " from " + old_avail[key] + " to " + new_avail[key] + "\n"
        with open(os.path.dirname(os.path.realpath(__file__)) + "/log.txt","a") as log_file:
            log_file.write(log)
        print "Updating DB... Check logs for changes"
        db.posts.remove()
        posts.insert(self.product_list)
        print "Done."
