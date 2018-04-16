
from scrapy.spiders import Spider
from scrapyspider.items import BaiKeItem
from scrapy import Request
from scrapy.selector import Selector
from urllib import parse
from re import sub
import json

class BaiKeSpider(Spider):

    name = 'baike'

    headers = {
        'User-Agent':
        'Mozilla/5.0 '
        '(Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    def start_requests(self):
        urls = 'https://baike.baidu.com/item/c语言/105958'
        yield Request(urls, headers=self.headers)



    def parse(self, response):
        sel = Selector(response)
        # sites = sel.xpath('//div[@class="main-content"]')
        item = BaiKeItem()

        item['name'] = sel.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()').extract()

        summary_paras = response.xpath('//div[@class="lemma-summary"]').xpath('div[@class="para"]')
        summary = ""
        for para_node in summary_paras:
            seg_list = para_node.re('>\s*(.*?)\s*<')
            # os._exit(233)  PS:scrapy里的list object在python里并不是list type

            for seg in seg_list:
                summary = "%s%s"%(summary,seg)

        summary=summary.replace("\n","")

        item['descrip'] = sub('\[\d+\]','',summary)

        info_names = sel.xpath('//dt[@class="basicInfo-item name"]/text()').extract()
        info_values = sel.xpath('//dd[@class="basicInfo-item value"]/text()').extract()

        count=0
        info_dict={}
        if len(info_names)!=len(info_values):
            print('Error in infobox: fail to match name and value')
        while count<len(info_names):
            tmp_name=info_names[count]
            tmp_value=info_values[count]
            info_dict[tmp_name.replace('\xa0','')]=tmp_value.replace('\xa0','')
            count+=1

        item['infobox']=json.dumps(info_dict, ensure_ascii=False)

        tag_node = sel.xpath('//dd[@id="open-tag-item"]/span')
        tag_list = []
        for tag_tmp in tag_node:
            tags = tag_tmp.re('>\s*(.*?)\s*<')
            x = ""
            for tag in tags:
                x = "%s%s" % (x, tag)
                # 如果存储了空串的话，把空串和有内容的字符串加起来就行
            tag_list.append(x)

        item['tag'] = tag_list

        # item['tag'] = sel.xpath('//dd[@id="open-tag-item"]/span/text()').extract()
        # 测试能否push

        keys = ['name', 'descrip', 'infobox', 'tag']
        for key in keys:
            item[key] = str(item[key]).replace('\n', '')  # 转换为字符串，好存进数据库

        yield item

        # extract links"/item..."注意链接此处还没有解码
        links = []
        for link in sel.xpath('//link/@href').re('.*\/item\/.*'):
            links.append(link)
        for link in sel.xpath('//a[@href]/@href').re('\/item\/.*'):
            links.append("https://baike.baidu.com%s"%link)

        print(links)

        for link in links:
            unquote_link=parse.unquote(link)
            request=Request(url=unquote_link,callback=self.parse,headers=self.headers,encoding='utf-8')
            yield request










