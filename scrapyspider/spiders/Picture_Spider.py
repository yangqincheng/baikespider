from scrapy.spiders import Spider
import re
from scrapy import Request
from scrapyspider.items import PictureItem

class Picture_Spider(Spider):
    name = 'picture'

    headers = {
        'User-Agent':
            'Mozilla/5.0 '
            '(Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    def start_requests(self):
        urls=['https://baike.baidu.com/item/%E9%B2%81%E8%BF%85/36231','https://baike.baidu.com/item/%E9%98%BF%E5%B0%94%E4%BC%AF%E7%89%B9%C2%B7%E7%88%B1%E5%9B%A0%E6%96%AF%E5%9D%A6']
        for url in urls:
            yield Request(url, headers=self.headers)

    def parse(self, response):

        list_imgs = response.xpath('//div[@class="summary-pic"]/a/img/@src').extract()
        item = PictureItem()
        if list_imgs:

            item ['image_urls'] = list_imgs
            yield item
