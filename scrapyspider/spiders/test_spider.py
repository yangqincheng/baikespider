import scrapy

import scrapy


# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
#     start_urls = [
#         'http://quotes.toscrape.com',
#     ]
#
#     def parse(self, response):
#         for quote in response.css('div.quote'):
#             yield {
#                 'text': quote.css('span.text::text').extract_first(),
#                 'author': quote.css('span small::text').extract_first(),
#                 'tags': quote.css('div.tags a.tag::text').extract(),
#             }
#
#         next_page = response.css('li.next a::attr(href)').extract_first()
#         if next_page is not None:
#             next_page = response.urljoin(next_page)
#             yield scrapy.Request(next_page, callback=self.parse)

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'https://baike.baidu.com/item/Python/407313',
    ]

    def parse(self, response):
        for line in response.css('div.body-wrapper'):
            yield {
                # 'text': quote.css('span.text::text').extract_first(),
                # 'author': quote.css('span small::text').extract_first(),
                # 'tags': quote.css('div.tags a.tag::text').extract(),
                'name': line.css('dd.lemmaWgt-lemmaTitle-title::text').extract_first()
            }

        # next_page = response.css('li.next a::attr(href)').extract_first()
        #
        # if next_page is not None:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(next_page, callback=self.parse)