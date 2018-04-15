from scrapy.spiders import Spider
from scrapyspider.items import DouBanMovieItem
from scrapy import Request
class DouBanMovieTop250Spider(Spider):
    name = 'douban_movie_top250'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    def start_requests(self):
        url = 'https://movie.douban.com/top250'

        yield Request(url, headers=self.headers)
        # yield迭代器


    def parse(self,response):
        item = DouBanMovieItem()
        movies = response.xpath('//ol[@class="grid_view"]/li')
        # //:从匹配选择的当前节点选择文档中的节点，而不考虑它们的位置。
        # @:选取属性
        # 因此该xpath语句的意义为:从ol节点中选取class="grid_view"的地方
        # .:选取当前节点
        for movie in movies:
            item['ranking'] = movie.xpath('.//div[@class="pic"]/em/text()').extract()[0]
            # 提取排名
            item['movie_name'] = movie.xpath('.//div[@class="hd"]/a/span[1]/text()').extract()[0]
            # 提取电影名
            item['score'] = movie.xpath('.//div[@class="star"]/span[@class="rating_num"]/text()').extract()[0]
            # 提取评分
            item['score_num'] = movie.xpath(
                './/div[@class="star"]/span/text()').re(r'(\d+)人评价')[0]
            # 提取评价人数  \d是正则表达式中匹配数字的方式，+匹配前面的子表达式一次或多次

            yield item

        next_url = response.xpath('//span[@class="next"]/a/@href').extract()
        if next_url:
            next_url = 'https://movie.douban.com/top250' + next_url[0]
            yield Request(next_url, headers=self.headers)


